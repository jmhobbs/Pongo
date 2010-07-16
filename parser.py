# -*- coding: utf-8 -*-

import re
import json

class EmptyQueryException ( Exception ):
	def __str__ ( self ):
		return "The query was empty."

class UnknownCommandException ( Exception ):
	def __init__ ( self, command, line ):
		self.command = command
		self.line = line

	def __str__ ( self ):
		return "Unknown Command \"%s\" on line %d" % ( self.command, self.line )

class SyntaxException ( Exception ):
	def __init__ ( self, error, line ):
		self.error = error
		self.line = line

	def __str__ ( self ):
		return "%s (line %d)" % ( self.error, self.line )

class ArgumentsException ( Exception ):
	def __init__ ( self, command, arg_count, arg_min, arg_max, line ):
		self.command = command
		self.arg_count = arg_count
		self.arg_min = arg_min
		self.arg_max = arg_max
		self.line = line

	def __str__ ( self ):
		return "Invalid number of arguments for %s on line %d. %d given, expects %d to %d." % ( self.command, self.line, self.arg_count, self.arg_min, self.arg_max )

class PongoParser:
	"""
	This is a totally naive parser built by someone who has no idea how actual parsers work.
	Please feel free to replace it :-)
	"""

	functions = {
		"find": { "name": "FIND", "operator": True, "arg-re": re.compile( r'^({.*})$' ), "min-args": 0, "max-args": 1 },
		"limit": { "name": "LIMIT", "operator": False, "arg-re": re.compile( r'^([0-9]+)$' ), "min-args": 1, "max-args": 1 },
	}

	operator = None
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

			if ')' != line[-1]:
				raise SyntaxException( "Missing close parenthesis.", i )

			# Get arguments
			arguments_raw = line.split( '(' )[1][:-1].strip()
			res = self.functions[command]['arg-re'].match( arguments_raw )

			if None != res:
				arguments = res.groups()
			else:
				arguments = ()

			# Go from strings to objects where needed
			adjusted_arguments = []
			for argument in arguments:
				try:
					adjusted_arguments.append( json.loads( argument ) )
				except:
					pass
			arguments = tuple( adjusted_arguments )

			# Check arguments
			if len( arguments ) < self.functions[command]['min-args'] or len( arguments ) > self.functions[command]['max-args']:
				raise ArgumentsException( command, len( arguments ), self.functions[command]['min-args'], self.functions[command]['max-args'], i )

			# Add to stack
			print command, arguments
			self.stack.append( ( command, arguments ) )

if __name__ == "__main__":

	query = """
find()
limit(10)

find( { "a": "b" } )
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
		print '-' * 20
		print p.stack
	except Exception, e:
		print "ERROR:", e
