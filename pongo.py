# -*- coding: utf-8 -*-

import pygtk
pygtk.require( '2.0' )
import gtk, gobject

import pymongo
import datetime

class Pongo:

	def destroy ( self, widget, data=None ):
		gtk.main_quit()

	def show_connection_dialog ( self ):
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
		host.set_text( "localhost" )
		host.show()
		dialog.vbox.pack_start( host )
		label = gtk.Label( "<b>Port</b>" )
		label.set_alignment( 0, 0 )
		label.set_use_markup( True )
		label.show()
		dialog.vbox.pack_start( label )
		port = gtk.Entry()
		port.set_text( "27017" )
		port.show()
		dialog.vbox.pack_start( port )
		response = dialog.run()
		dialog.hide()
		
		if response == gtk.RESPONSE_ACCEPT:
			self.mongo_connect( host.get_text(), int( port.get_text() ) )

	def database_picked ( self, treeview, path, view_column ):
		i = self.databases_model.get_iter( path )
		self.database_name = self.databases_model.get_value( i, 0 )
		self.log( "Selected database: %s" % self.database_name )
		self.load_collections()
		self.window.set_title( "Pongo > %s:%d > %s" % ( self.host, self.port, self.database_name ) )

	def load_collections ( self ):
		self.collections_model.clear()
		for collection in self.connection[self.database_name].collection_names():
			i = self.collections_model.append()
			self.collections_model.set( i, 0, collection )

	def collection_picked ( self, treeview, path, view_column ):
		i = self.collections_model.get_iter( path )
		self.collection_name = self.collections_model.get_value( i, 0 )
		self.log( "Selected collection: %s" % self.collection_name )
		self.window.set_title( "Pongo > %s:%d > %s > %s" % ( self.host, self.port, self.database_name, self.collection_name ) )

	def __init__ ( self ):
		self.window = gtk.Window( gtk.WINDOW_TOPLEVEL )
		self.window.connect( "destroy", self.destroy )
		self.window.set_title( "Pongo" )

		# Build all the panes we need
		self.base_pane = gtk.VPaned()
		self.top_pane = gtk.HPaned()
		self.left_pane = gtk.VPaned()
		self.right_pane = gtk.VPaned()

		# Get the panes in place
		self.top_pane.add( self.left_pane )
		self.top_pane.add( self.right_pane )
		self.base_pane.add( self.top_pane )

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
		self.base_pane.add( scrolled_window )

		# Build the Query Pane
		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )
		self.query = gtk.TextView()
		self.query_buffer = self.query.get_buffer()
		scrolled_window.add( self.query )
		self.left_pane.add( scrolled_window )

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
		self.right_pane.add( scrolled_window )

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
		self.right_pane.add( scrolled_window )

		# And go!
		self.window.add( self.base_pane )
		self.window.show_all()

		self.show_connection_dialog()

	def log ( self, message ):
		i = self.log_model.prepend()
		self.log_model.set( i, 0, datetime.datetime.now().strftime( '%T' ) )
		self.log_model.set( i, 1, message )

	def mongo_connect ( self, host="localhost", port=27017 ):

		self.host = host
		self.port = port
		self.window.set_title( "Pongo > %s:%d" % ( self.host, self.port ) )

		self.log( "Connecting to %s:%d" % ( host, port ) )
		self.connection = pymongo.Connection()
		self.log( "Reading database list." )
		for database in self.connection.database_names():
			i = self.databases_model.append()
			self.databases_model.set( i, 0, database )

	def main( self ):
		gtk.main()

if __name__ == "__main__":
	app = Pongo()
	app.main()
