# -*- coding: utf-8 -*-

import pygtk
pygtk.require( '2.0' )
import gtk, gobject

import pymongo
import datetime

class PongoObject ( gtk.Frame ):
	
	def __init__ ( self ):
		gtk.Frame.__init__( self )
		self.store = gtk.TreeStore( str, str )
		
		tree_view = gtk.TreeView( self.store )
		
		cell = gtk.CellRendererText()
		column = gtk.TreeViewColumn( "Key", cell, text=0 )
		tree_view.append_column( column )
		
		cell = gtk.CellRendererText()
		column = gtk.TreeViewColumn( "Value", cell, text=1 )
		tree_view.append_column( column )
		
		tree_view.set_enable_tree_lines( True )
		#tree_view.set_headers_visible( False )
		
		self.add( tree_view )
		
		self.base = self.store.append( None, [ '[Object]', '' ] )
	
	def load ( self, obj ):
		self.load_dict( obj, self.base )

	def load_dict ( self, data, iterator ):
		for key,value in data.items():
			self.process_item( key, value, iterator )

	def load_tuple ( self, data, iterator ):
		i = 0
		for item in data:
			self.process_item( '[%d]' % i, item, iterator )
			i = i + 1

	def process_item ( self, key, value, iterator ):
		if dict == type( value ):
			new_iterator = self.store.append( iterator, [ key, '[Object]' ] )
			self.load_dict( value, new_iterator )
		elif tuple == type( value ) or list == type( value ):
			new_iterator = self.store.append( iterator, [ key, '[Array]' ] )
			self.load_tuple( value, new_iterator )
		else:
			self.store.append( iterator, [ key, value ] )

class Pongo:

	# Establish variables
	mongo = None
	database = None
	collection = None
	host = "localhost"
	port = 27017

	def build_title ( self ):
		if None != self.collection:
			self.window.set_title( "Pongo > %s:%d > %s > %s" % ( self.host, self.port, self.database, self.collection ) )
		elif None != self.database:
			self.window.set_title( "Pongo > %s:%d > %s" % ( self.host, self.port, self.database ) )
		elif None != self.mongo:
			self.window.set_title( "Pongo > %s:%d" % ( self.host, self.port ) )
		else:
			self.window.set_title( "Pongo" )

	def show_connection_dialog ( self, menuitem=None ):
		dialog = gtk.Dialog(
			"Pongo - Connect",
			None,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			(
				"Connect", gtk.RESPONSE_ACCEPT,
				"Cancel", gtk.RESPONSE_CLOSE
			)
		)
		
		label = gtk.Label( "<b>Host</b>" )
		label.set_alignment( 0, 0 )
		label.set_use_markup( True )
		label.show()
		dialog.vbox.pack_start( label )
		
		host = gtk.Entry()
		host.set_text( self.host )
		host.show()
		dialog.vbox.pack_start( host )
		
		label = gtk.Label( "<b>Port</b>" )
		label.set_alignment( 0, 0 )
		label.set_use_markup( True )
		label.show()
		dialog.vbox.pack_start( label )
		
		port = gtk.Entry()
		port.set_text( str( self.port ) )
		port.show()
		dialog.vbox.pack_start( port )
		
		response = dialog.run()
		dialog.hide()
		
		if response == gtk.RESPONSE_ACCEPT:
			self.mongo_connect( host.get_text(), int( port.get_text() ) )

	def database_picked ( self, treeview, path, view_column ):
		i = self.databases_model.get_iter( path )
		self.database = self.databases_model.get_value( i, 0 )
		self.log( "Selected database: %s" % self.database )
		self.load_collections()
		self.build_title()

	def load_collections ( self ):
		self.collections_model.clear()
		for collection in self.mongo[self.database].collection_names():
			i = self.collections_model.append()
			self.collections_model.set( i, 0, collection )

	def collection_picked ( self, treeview, path, view_column ):
		i = self.collections_model.get_iter( path )
		self.collection = self.collections_model.get_value( i, 0 )
		self.log( "Selected collection: %s.%s" % ( self.database, self.collection ) )
		self.build_title()

	def __init__ ( self ):
		self.window = gtk.Window( gtk.WINDOW_TOPLEVEL )
		self.window.connect( "destroy", lambda w: gtk.main_quit() )
		self.window.set_title( "Pongo" )
		self.window.set_size_request( 700, 500 )

		# Build all the panes we need
		base_pane = gtk.VPaned()
		top_pane = gtk.HPaned()
		left_pane = gtk.VPaned()
		right_pane = gtk.VPaned()
		
		# Now the complete container
		contain_all = gtk.VBox( False, 0 )
		self.window.add( contain_all )
		contain_all.pack_end( base_pane, True, True, 2 )

		# Build the menu
		self.menu_connect = gtk.MenuItem( "Connect" )
		self.menu_refresh = gtk.MenuItem( "Refresh" )
		self.menu_bar = gtk.MenuBar()
		contain_all.pack_start( self.menu_bar, False, False, 2 )
		self.menu_bar.append( self.menu_connect )
		self.menu_bar.append( self.menu_refresh )
		self.menu_connect.connect( "activate", self.show_connection_dialog )

		# Get the panes in place
		top_pane.add( left_pane )
		top_pane.add( right_pane )
		base_pane.add( top_pane )

		# Build the Logs Pane
		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )
		self.log_model = gtk.ListStore( gobject.TYPE_STRING, gobject.TYPE_STRING )
		log_view = gtk.TreeView( self.log_model )
		scrolled_window.add_with_viewport( log_view )
		cell = gtk.CellRendererText()
		column = gtk.TreeViewColumn( "Log", cell, text=0 )
		log_view.append_column( column )
		column = gtk.TreeViewColumn( "", cell, text=1 )
		log_view.append_column( column )
		base_pane.add( scrolled_window )

		# Build the Query Pane
		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )
		self.query = gtk.TextView()
		scrolled_window.add( self.query )
		left_pane.add( scrolled_window )

		# Build the Databases Pane
		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )
		self.databases_model = gtk.ListStore( gobject.TYPE_STRING )
		databases_view = gtk.TreeView( self.databases_model )
		databases_view.connect( "row-activated", self.database_picked )
		scrolled_window.add_with_viewport( databases_view )
		cell = gtk.CellRendererText()
		column = gtk.TreeViewColumn( "Databases", cell, text=0 )
		databases_view.append_column( column )
		right_pane.add( scrolled_window )

		# Build the Collections Pane
		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )
		self.collections_model = gtk.ListStore( gobject.TYPE_STRING )
		collections_view = gtk.TreeView( self.collections_model )
		collections_view.connect( "row-activated", self.collection_picked )
		scrolled_window.add_with_viewport( collections_view )
		cell = gtk.CellRendererText()
		column = gtk.TreeViewColumn( "Collections", cell, text=0 )
		collections_view.append_column( column )
		right_pane.add( scrolled_window )

		# And go!
		self.window.show_all()

		self.show_connection_dialog()

	def log ( self, message ):
		i = self.log_model.prepend()
		self.log_model.set( i, 0, datetime.datetime.now().strftime( '%T' ) )
		self.log_model.set( i, 1, message )

	def mongo_connect ( self, host="localhost", port=27017 ):

		self.mongo_disconnect()

		self.host = host
		self.port = port

		self.log( "Connecting to %s:%d" % ( host, port ) )
		try:
			self.mongo = pymongo.Connection( host, port )
			for database in self.mongo.database_names():
				i = self.databases_model.append()
				self.databases_model.set( i, 0, database )
			self.build_title()
		except:
			self.log( "Connection failed!" )
			self.mongo_disconnect()

	def mongo_disconnect ( self ):
		self.mongo = None
		self.database = None
		self.collection = None
		
		self.databases_model.clear()
		self.collections_model.clear()
		
		self.build_title()

	def main( self ):
		gtk.main()

if __name__ == "__main__":
	app = Pongo()
	app.main()
