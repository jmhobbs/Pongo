# -*- coding: utf-8 -*-

import pygtk
pygtk.require( '2.0' )
import gtk, gobject

class PongoTreeViewTest:

	sample_data = { 'a': 'string', 'b': 5, 'c': True, 'd': [ 'e', 6, 5.4, False, { 'f': 'g', 'h': [ 'i', 'j', 'k', 7 ] } ] }

	def __init__ ( self ):
		self.window = gtk.Window( gtk.WINDOW_TOPLEVEL )
		self.window.connect( "destroy", lambda w: gtk.main_quit() )
		self.window.set_title( "Pongo TreeView Test" )
		self.window.set_size_request( 700, 500 )

		self.tree_store = gtk.TreeStore( str, str )

		tree_view = gtk.TreeView( self.tree_store )
		cell = gtk.CellRendererText()
		column = gtk.TreeViewColumn( "Key", cell, text=0 )
		tree_view.append_column( column )
		cell = gtk.CellRendererText()
		column = gtk.TreeViewColumn( "Value", cell, text=1 )
		tree_view.append_column( column )
		tree_view.set_enable_tree_lines( True )
		tree_view.set_headers_visible( False )

		it = self.tree_store.append( None, [ '[Object]', '' ] )
		self.load_dict( self.sample_data, it )

		self.window.add( tree_view )

		self.window.show_all()

	def load_dict ( self, data, iterator ):
		for key,value in data.items():
			self.process_item( key, value, iterator )

	def load_tuple ( self, data, iterator ):
		i = 0
		for item in data:
			self.process_item( i, item, iterator )
			i = i + 1


	def process_item ( self, key, value, iterator ):
		if dict == type( value ):
			new_iterator = self.tree_store.append( iterator, [ key, '[Object]' ] )
			self.load_dict( value, new_iterator )
		elif tuple == type( value ) or list == type( value ):
			new_iterator = self.tree_store.append( iterator, [ key, '[Array]' ] )
			self.load_tuple( value, new_iterator )
		else:
			self.tree_store.append( iterator, [ key, value ] )


	def main( self ):
		gtk.main()

if __name__ == "__main__":
	app = PongoTreeViewTest()
	app.main()
