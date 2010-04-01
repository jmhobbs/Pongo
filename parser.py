# -*- coding: utf-8 -*-

class EmptyQueryException ( Exception ):
	def __str__ ( self ):
		return "The query was empty."

class UnknownCommandException ( Exception ):
	def __init__ ( self, command, line ):
		self.command = command
		self.line = line

	def __str__ ( self ):
		return "Unknown Command \"%s\" on line %d" % ( self.command, self.line )


class PongoParser:
	"""
	This is a totally naive parser built by someone who has no idea how actual parsers work.
	Please feel free to replace it :-)
	"""

	functions = {
		# token: ( NAME, min-params, max-params )
		"find": ( "FIND", 0, 2 ),
		"limit": ( "LIMIT", 1, 1 )
	}

	stack = []

	# Intermediary members
	query = ()
	lines = ()

	def parse ( self, query ):
		self.query = query;
		if 0 == self._extract():
			raise EmptyQueryException();
		self._build_stack()

	def _extract ( self ):
		self.lines = self.query.split( "\n" )
		i = 0
		j = 0
		for line in self.lines:
			if 0 == len( line.strip() ):
				self.lines[i] = None
			else:
				j = j + 1
			i = i + 1
		return j

	def _build_stack ( self ):
		i = -1
		for line in self.lines:
			i = i + 1
			if line == None:
				continue;
			command = line.split( '(' )[0].lower()
			if command not in self.functions.keys():
				raise UnknownCommandException( command, i + 1 ) # i + 1 translates list index to line number

		# Get arguments
		# Check arguments
		# Add to stack


if __name__ == "__main__":

	query = """
find()
limit(10)
"""

	print "=" * 20
	print "  Pongo Parser Tests"
	print "=" * 20
	print "  Query"
	print "=" * 20
	print query
	print "=" * 20

	p = PongoParser()
	try:
		p.parse( query )
	except Exception, e:
		print "ERROR:", e