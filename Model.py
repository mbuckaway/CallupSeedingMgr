
import os
import re
import sys
import datetime
import iso3166
import random
from collections import defaultdict
from metaphone import doublemetaphone
from Excel import GetExcelReader
import Utils

countryTranslations = {
	'England':						'United Kingdom',
	'Great Britain':				'United Kingdom',
	'Scotland':						'United Kingdom',
	'Wales':						'United Kingdom',
	'United States of America': 	'United States',
	'Hong Kong, China':				'Hong Kong',
}
countryTranslations = { k.upper(): v for k, v in countryTranslations.iteritems() }

specialNationCodes = {
	u'Chinese Taipei':		'TPE',	# For some reason, the UCI thinks Taipei is a country and not the capital of Taiwan.
}
specialNationCodes = { k.upper(): v for k, v in specialNationCodes.iteritems() }

class Result( object ):
	ByPoints, ByPosition = (0, 1)
	
	Fields = (
		'bib',
		'first_name', 'last_name',
		'team',
		'uci_code',
		'license',
		'nation',
		'nation_code', 
		'age',
		'date_of_birth',
		'points', 'position',
		'row'
	)
	NumericFields = set([
		'bib', 'age', 'points', 'position'
	])

	def __init__( self, **kwargs ):
		
		if 'name' in kwargs:
			# find the last lower-case letter.  Assume that is the last char in the first_name
			name = kwargs['name']
			j = 0
			for i, c in enumerate(name):
				if c.isalpha() and c.islower() and name[i+1:i+2] == u' ':
					j = i + 1
			kwargs['first_name'] = name[:j]
			kwargs['last_name'] = name[j:]
		
		for f in self.Fields:
			setattr( self, f, kwargs.get(f, None) )
			
		if self.license is not None:
			self.license = unicode(self.license).strip()
			
		if self.position:
			try:
				self.position = int(self.position)
			except ValueError:
				self.position = None
				
		if self.row:
			try:
				self.row = int(self.row)
			except ValueError:
				self.row = None
				
		if self.points:
			try:
				self.points = float(self.points)
			except ValueError:
				self.points = None
		
		if self.last_name:
			self.last_name = unicode(self.last_name).replace(u'*',u'').strip()
			
		if self.first_name:
			self.first_name = unicode(self.first_name).replace(u'*',u'').replace(u'(JR)',u'').strip()
		
		# Get the 3-digit nation code from the nation name.
		if self.nation:
			self.nation = unicode(self.nation).replace( u'&', u'and' ).strip()
			self.nation = countryTranslations.get(self.nation.upper(), self.nation)
			if not self.nation_code:
				try:
					self.nation_code = unicode(specialNationCodes.get(self.nation.upper(), iso3166.countries.get(self.nation).alpha3))
				except KeyError:
					raise KeyError( u'cannot find nation_code from nation: {}'.format(self.nation) )
		
		if self.uci_code:
			self.uci_code = unicode(self.uci_code).strip()
			if len(self.uci_code) != 11:
				raise ValueError( u'invalid uci_code: {}'.format(self.uci_code) )
			
			if not self.date_of_birth:
				self.date_of_birth = datetime.date( int(self.uci_code[3:7]), int(self.uci_code[7:9]), int(self.uci_code[9:11]) )
				
			if not self.nation_code:
				self.nation_code = self.uci_code[:3]
		else:
			if self.nation_code and self.date_of_birth:
				self.uci_code = u'{}{}'.format( self.nation_code, self.date_of_birth.strftime('%Y%m%d') )
			
		if self.date_of_birth and not self.age:
			self.age = datetime.date.today().year - self.date_of_birth.year		# Competition age.
		
		if self.age is not None:
			try:
				self.age = int(self.age)
			except ValueError:
				raise ValueError( u'invalid age: {}'.format(self.age) )
				
		assert self.date_of_birth is None or isinstance(self.date_of_birth, datetime.date), 'invalid Date of Birth'
		
		self.cmp_policy = None
	
	def __repr__( self ):
		'''
		return Utils.removeDiacritic(
			u'Result({})'.format( ', '.join( u'{}={}'.format(f,
				getattr(self,f,None) if not isinstance(getattr(self,f,None), unicode) else u'"{}"'.format(getattr(self,f,None))) for f in self.Fields)
			)
		'''
		return '({})'.format( Utils.removeDiacritic( self.as_str(self.Fields) ) )
		
	def as_str( self, fields=None ):
		fields = fields or self.Fields
		return u', '.join( unicode(getattr(self,f).upper() if f == 'last_name' else getattr(self,f)) for f in fields if getattr(self,f,None) is not None and f != 'row' )
	
	@property
	def full_name( self ):
		return u'{} {}'.format( self.first_name, self.last_name )
	
	def get_key( self ):
		if self.cmp_policy == self.ByPoints:
			return -(self.points or 0)
		elif self.cmp_policy == self.ByPosition:
			return self.position or sys.maxint
		assert False, 'Invalid cmp_policy'
		
	def get_value( self ):
		if self.cmp_policy == self.ByPoints:
			return self.points
		elif self.cmp_policy == self.ByPosition:
			return self.position
		assert False, 'Invalid cmp_policy'

reAlpha = re.compile( '[^A-Z]+' )
header_sub = {
	u'RANK':	u'POSITION',
	u'POS':		u'POSITION',
	u'BIBNUM':	u'BIB',
	u'DOB':		u'DATEOFBIRTH',
}
def scrub_header( h ):
	h = reAlpha.sub( '', Utils.removeDiacritic(unicode(h)).upper() )
	return header_sub.get(h, h)

class FindResult( object ):
	NoMatch, Success, SuccessSoundalike, MultiMatch = range(4)

	def __init__( self, search, matches, source, soundalike ):
		self.search = search
		self.matches = sorted(matches, key = lambda r: r.row)
		self.source = source
		self.soundalike = soundalike
		
	def get_key( self ):
		if len(self.matches) == 1:
			return self.matches[0].get_key()
		return 0 if self.source.cmp_policy == Result.ByPoints else sys.maxint
			
	def get_value( self ):
		if not self.matches:
			return u''
		if len(self.matches) == 1:
			return self.matches[0].get_value()
		return u"\u2605" * len(self.matches)
	
	def get_status( self ):
		if not self.matches:
			return self.NoMatch
		if len(self.matches) == 1:
			if self.soundalike:
				return self.SuccessSoundalike
			return self.Success
		return self.MultiMatch
	
	def __repr__( self ):
		return self.get_value()
	
class Source( object ):
	Indices = (
		'by_license', 'by_uci_code',
		'by_last_name', 'by_first_name',
		'by_mp_last_name', 'by_mp_first_name',
		'by_nation_code', 'by_date_of_birth', 'by_age',
	)
	def __init__( self, fname, sheet_name, soundalike = True ):
		self.fname = fname
		self.sheet_name = sheet_name
		self.soundalike = soundalike
		self.results = []
		self.hasField = set()
		self.cmp_policy = None
		for i in self.Indices:
			setattr( self, i, defaultdict(set) )
	
	def empty( self ):
		return not self.results
	
	def field_from_index( self, i ):
		return i[6:] if i.startswith('by_mp_') else i[3:]
		
	def get_cmp_policy_field( self ):
		if self.cmp_policy == Result.ByPoints:
			return 'points'
		elif self.cmp_policy == Result.ByPosition:
			return 'position'
		else:
			return None
		
	def read( self ):
		reader = GetExcelReader( self.fname )
		header_fields = ['name'] + list(Result.Fields)
		header_map = {}
		errors = []
		for row_number, row in enumerate(reader.iter_list(self.sheet_name)):
			if not row:
				continue
			
			# Map the column headers to the standard fields.
			if not header_map:
				for c, v in enumerate(row):
					rv = scrub_header( v )
					
					for h in header_fields:
						hv = scrub_header( h )
						if rv == hv:
							header_map[h] = c
							break
				continue
		
			try:
				if all( not row[i] for i in xrange(3) ):
					continue
			except IndexError:
				continue
		
			# Create a Result from the row.
			row_fields = {}
			for field, column in header_map.iteritems():
				try:
					row_fields[field] = row[column]
				except IndexError:
					pass
			
			# If points and position are not specified, use the row_number as the position.
			if 'points' not in row_fields and 'position' not in row_fields:
				row_fields['position'] = row_number + 1
				
			row_fields['row'] = row_number + 1
				
			try:
				result = Result( **row_fields )
			except Exception as e:
				errors.append( '{}::{} row {}: {}'.format(self.fname, self.sheet_name, row_number+1, e) )
				continue
			
			result.row_number = row_number
			self.add( result )
		
		self.cmp_policy = Result.ByPoints if 'points' in self.hasField else Result.ByPosition
		for r in self.results:
			r.cmp_policy = self.cmp_policy
		
		return errors
		
	def get_ordered_fields( self ):
		return tuple(f for f in Result.Fields if f in self.hasField and f not in ('points', 'position', 'row'))
	
	def randomize_positions( self ):
		positions = range( 1, len(self.results)+1 )
		random.shuffle( positions )
		self.cmp_policy = Result.ByPosition
		for i, r in enumerate(self.results):
			r.cmp_policy = self.cmp_policy
			r.position = positions[i]

	def add( self, result ):
		self.results.append( result )
		
		'''
		'by_license', 'by_uci_code',
		'by_last_name', 'by_first_name',
		'by_mp_last_name', 'by_mp_first_name',
		'by_nation_code', 'by_date_of_birth', 'by_age',
		'''
		
		for field in Result.Fields:
			if getattr( result, field, None ):
				self.hasField.add( field )
		
		for idx_name in self.Indices:
			field = self.field_from_index(idx_name)
			v = getattr( result, field, None )
			if not v:
				continue
			idx = getattr( self, idx_name )
				
			if idx_name.startswith( 'by_mp_' ):	# Initialize a doublemetaphone (soundalike) index.
				for mp in doublemetaphone(v.encode('utf8')):
					if mp:
						idx[mp].add( result )
			else:							# Initialize a regular field index.
				assert idx_name != 'by_license' or v not in idx, 'Duplicate license: {}'.format(v)
				try:
					idx[Utils.removeDiacritic(v).upper()].add( result )
				except:
					idx[v].add( result )
	
	def match_indices( self, search, indices ):
		# Look for a set intersection of one element between all source criteria.
		soundalike = False
		setCur = None
		for idx_name in indices:
			idx = getattr( self, idx_name )
			v = getattr( search, self.field_from_index(idx_name), None )
			if not v or not idx:
				setCur = None
				break
			
			try:
				v = Utils.removeDiacritic(v).upper()
			except:
				pass
				
			found = set()
			if idx_name.startswith( 'by_mp_' ):
				soundalike = True
				for mp in doublemetaphone(v.encode('utf8')):
					if mp and mp in idx:
						found |= idx[mp]
			elif v in idx:
				found = idx[v]
			
			if setCur is None:
				setCur = found
			else:
				setCur &= found
			
			if not setCur:
				break
		
		return FindResult( search, setCur, self, soundalike )
		
	def find( self, search ):
		''' Returns (result, messages) - result will be None if no match. '''

		# First check for a common License field.  If so, attempt to match it exactly and stop.
		pi = ['by_license']
		if all( self.field_from_index(i) in self.hasField for i in pi ):
			return self.match_indices( search, pi )
		
		# If no license code, try find a perfect, unique match based on the following fields.
		perfectIndices = (
			('by_last_name', 'by_first_name', 'by_uci_code', ),
			('by_last_name', 'by_first_name', 'by_nation_code', 'by_age', ),
		)
		for pi in perfectIndices:
			if all( self.field_from_index(i) in self.hasField for i in pi ):
				findResult = self.match_indices( search, pi )
				if findResult.get_status() == FindResult.Success:
					return findResult
			
		# Failover: try to find a soundalike on a number of fields.
		indices = []
		if self.soundalike:
			potentialIndices = (
				('by_mp_last_name', 'by_mp_first_name', 'by_uci_code', ),
				('by_mp_last_name', 'by_mp_first_name', 'by_nation_code', 'by_age',),
				('by_mp_last_name', 'by_nation_code', 'by_age',),
			)
			
			for pi in potentialIndices:
				if all( self.field_from_index(i) in self.hasField for i in pi ):
					indices = pi
					break
		
		if indices:
			return self.match_indices( search, indices )
		
		# Finally, do a special check so to match if there is only first name, last name.
		lastDitchIndices = (
			('by_last_name', 'by_first_name',),
			('by_mp_last_name', 'by_mp_first_name',),
		)
		for pi in lastDitchIndices:
			if not self.soundalike and any(i.startswith('by_mp_') for i in pi):
				continue
			if all( self.field_from_index(i) in self.hasField for i in pi ):
				findResult = self.match_indices( search, pi )
				if findResult.status() != findResult.NoMatch:
					return findResult
		
		return FindResult( search, [], self, False )
	
class ResultCollection( object ):
	def __init__( self ):
		self.sources = []
		
	def add_source( self, source ):
		self.sources.append( source )
		
if __name__ == '__main__':
	s = Source( 'CallupTest.xlsx', '2014 Result' )
	errors = s.read()
	print s.by_mp_last_name
	sys.exit()
	
	#for r in s.results:
	#	print r
	for k, v in sorted( ((k, v) for k, v in s.by_mp_last_name.iteritems()), key=lambda x: x[0] ):
		print '{}: {}'.format(k, ', '.join( Utils.removeDiacritic(r.full_name) for r in v ))
	for k, v in sorted( ((k, v) for k, v in s.by_mp_first_name.iteritems()), key=lambda x: x[0] ):
		print '{}: {}'.format(k, ', '.join( Utils.removeDiacritic(r.full_name) for r in v ))
		
	for r in s.results:
		for p_last in doublemetaphone(r.last_name.encode('utf8')):
			if not p_last:
				continue
			p_last_set = s.by_mp_last_name[p_last]
			for p_first in doublemetaphone(r.first_name.encode('utf8')):
				p_first_set = s.by_mp_first_name[p_first]
				p_last_first_set = p_last_set & p_first_set
				if len(p_last_first_set) > 1:
					print ', '.join( u'({}, {}, {})'.format(
							Utils.removeDiacritic(rr.full_name), Utils.removeDiacritic(rr.nation_code), rr.age,
						)
						for rr in p_last_first_set )

	
