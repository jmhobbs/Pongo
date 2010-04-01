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
		self.build_title()

	def __init__ ( self ):
		self.window = gtk.Window( gtk.WINDOW_TOPLEVEL )
		self.window.connect( "destroy", lambda w: gtk.main_quit() )
		self.window.set_title( "Pongo" )
		self.window.set_size_request( 700, 500 )

		# Build the layout
		base = gtk.VBox()
		h_pane = gtk.HPaned()
		right_pane = gtk.VPaned()
		h_pane.pack2( right_pane )
		self.window.add( base )

		# Build the menu
		menu = gtk.Menu()

		file_menu = gtk.MenuItem( "File" )
		file_menu.set_submenu( menu )

		self.menu_connect = gtk.MenuItem( "Connect" )
		self.menu_connect.connect( "activate", self.show_connection_dialog )

		self.menu_disconnect = gtk.MenuItem( "Disconnect" )
		self.menu_disconnect.connect( "activate", self.mongo_disconnect )

		self.menu_refresh = gtk.MenuItem( "Refresh" )
		# TODO Connect this?

		self.menu_exit = gtk.MenuItem( "Exit" )
		self.menu_exit.connect( "activate", lambda w: gtk.main_quit() )

		menu.append( self.menu_connect )
		menu.append( self.menu_disconnect )
		menu.append( self.menu_refresh )
		menu.append( self.menu_exit )

		self.menu_bar = gtk.MenuBar()
		self.menu_bar.append( file_menu )
		base.pack_start( self.menu_bar, False, False, 5 )

		# Build the results window
		self.results_window = gtk.VBox()
		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )
		scrolled_window.set_size_request( 500, 100 )
		scrolled_window.add_with_viewport( self.results_window )
		h_pane.pack1( scrolled_window )

		# Build the status bar
		self.status = gtk.Statusbar()
		base.pack_end( self.status, False, False, 0 )
		self.status.push( self.status.get_context_id( 'welcome' ), 'Welcome to Pongo' )

		# Now add the main pane
		base.pack_end( h_pane, True, True, 0 )

		# Build the Query box
		hbox = gtk.HBox()
		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )
		self.query = gtk.TextView()
		scrolled_window.add( self.query )
		frame = gtk.Frame()
		frame.add( scrolled_window )
		frame.set_size_request( 100, 100 )
		self.run_button = gtk.Button( "Run" )
		self.run_button.set_size_request( 100, 100 )
		hbox.pack_end( self.run_button, False, False, 5 )
		hbox.pack_start( frame, True, True, 5 )
		base.pack_start( hbox, False, False, 5 )

		# Build the Databases Pane
		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )
		scrolled_window.set_size_request( 100, 150 )
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

	def add_result ( self, data ):
		obj = PongoObject()
		obj.load( data )
		obj.show_all()
		self.results_window.pack_start( obj, True, True, 5 )

	def mongo_connect ( self, host="localhost", port=27017 ):

		self.mongo_disconnect()

		self.host = host
		self.port = port

		try:
			self.mongo = pymongo.Connection( host, port )
			for database in self.mongo.database_names():
				i = self.databases_model.append()
				self.databases_model.set( i, 0, database )
			self.build_title()
			self.set_status( "Connected to %s:%d" % ( self.host, self.port ) )
		except:
			self.mongo_disconnect()
			self.set_status( "Connection failed to %s:%d" % ( self.host, self.port ) )

	def mongo_disconnect ( self, w=None ):
		self.set_status( "Disconnected from %s:%d" % ( self.host, self.port ) )
		self.mongo = None
		self.database = None
		self.collection = None

		self.databases_model.clear()
		self.collections_model.clear()

		self.build_title()

	def set_status ( self, message ):
		context = self.status.get_context_id( 'welcome' )
		self.status.pop( context )
		self.status.push( context, message )

	def main( self ):
		gtk.main()

if __name__ == "__main__":
	app = Pongo()
	app.main()
