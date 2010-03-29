# -*- coding: utf-8 -*-

import pygtk
pygtk.require( '2.0' )
import gtk, gobject

import pymongo
import datetime

class Pongo:

	def destroy ( self, widget, data=None ):
		gtk.main_quit()

	def __init__ ( self ):
		self.window = gtk.Window( gtk.WINDOW_TOPLEVEL )
		self.window.connect( "destroy", self.destroy )

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
		scrolled_window.add_with_viewport( collections_view )
		cell = gtk.CellRendererText()
		column = gtk.TreeViewColumn( "Collections", cell, text=0 )
		collections_view.append_column( column )
		self.right_pane.add( scrolled_window )

		# And go!
		self.window.add( self.base_pane )
		self.window.show_all()

		self.connect()

	def log ( self, message ):
		i = self.log_model.prepend()
		self.log_model.set( i, 0, datetime.datetime.now().strftime( '%T' ) )
		self.log_model.set( i, 1, message )

	def connect ( self, host="localhost", port=27017 ):
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
