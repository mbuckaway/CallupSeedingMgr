
import os
import re
import sys
import six
import datetime
import iso3166
import random
import traceback
from metaphone import doublemetaphone
from Excel import GetExcelReader
from CountryIOC import uci_country_codes, uci_country_codes_set
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

specialNationCodes = uci_country_codes
specialNationCodes.update( {
		u'Chinese Taipei':		'TPE',
	}
)
specialNationCodes = { k.upper(): v for k, v in specialNationCodes.iteritems() }

all_quotes = re.compile( u"[\u2019\u0027\u2018\u201C\u201D`\"]", re.UNICODE )
all_stars = re.compile( u"[*\u2605\u22C6]" )
def normalize_name( s ):
	s = all_quotes.sub( u"'", unicode(s).replace(u'(JR)',u'') )
	s = all_stars.sub( u"", s )
	return s.strip()
	
def normalize_name_lookup( s ):
	return Utils.removeDiacritic(normalize_name(s)).upper()

today = datetime.date.today()
earliest_year = (today - datetime.timedelta( days=106*365 )).year
latest_year = (today - datetime.timedelta( days=7*365 )).year
invalid_date_of_birth = datetime.date(1900, 1, 1)
def date_from_value( s ):
	if isinstance(s, datetime.date):
		return s
	if isinstance(s, datetime.datetime):
		return s.date()
	
	if isinstance(s, (float, int)):
		return datetime.date( *(xldate_as_tuple(s, datemode)[:3]) )
		
	try:
		s = s.replace('-', '/')
	except:
		pass
	
	# Start with month, day, year format.
	try:
		mm, dd, yy = [int(v.strip()) for v in s.split('/')]
	except:
		return invalid_date_of_birth
	
	if mm > 1900:
		# Switch to yy, mm, dd format.
		yy, mm, dd = mm, dd, yy
	
	# Correct for 2-digit year.
	for century in [0, 1900, 2000, 2100]:
		if earliest_year <= yy + century <= latest_year:
			yy += century
			break
	
	# Check if day and month are reversed.
	if mm > 12:
		dd, mm = mm, dd
		
	assert 1900 <= yy
		
	try:
		return datetime.date( year=yy, month=mm, day=dd )
	except Exception as e:
		print yy, mm, dd
		raise e
		

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
	KeyFields = set([
		'first_name', 'last_name',
		'uci_code', 'license', 'nation_code', 'age',
	])

	def __init__( self, **kwargs ):
		
		if 'name' in kwargs and 'last_name' not in kwargs:
			name = normalize_name( kwargs['name'] )
			
			# Check that there are at least two consecutive capitalized characters in the name somewhere.
			for i in xrange(len(name)-1):
				chars2 = name[i:i+1]
				if chars2.isalpha() and chars2 == chars2.upper():
					break
			else:
				raise ValueError( u'invalid name: last name must be capitalized: {}'.format( name ) )
			
			# Find the last alpha character.
			cLast = 'C'
			for i in xrange(len(name)-1, -1, -1):
				if name[i].isalpha():
					cLast = name[i]
					break
			
			if cLast == cLast.lower():
				# Assume the name is of the form LAST NAME First Name.
				# Find the last upper-case letter preceding a space.  Assume that is the last char in the last_name.
				j = 0
				i = 0
				while 1:
					i = name.find( u' ', i )
					if i < 0:
						if not j:
							j = len(name)
						break
					cPrev = name[i-1]
					if cPrev.isalpha() and cPrev.isupper():
						j = i
					i += 1
				kwargs['last_name'] = name[:j]
				kwargs['first_name'] = name[j:]
			else:
				# Assume the name field is of the form First Name LAST NAME
				# Find the last lower-case letter preceding a space.  Assume that is the last char in the first_name.
				j = 0
				i = 0
				while 1:
					i = name.find( u' ', i )
					if i < 0:
						break
					cPrev = name[i-1]
					if cPrev.isalpha() and cPrev.islower():
						j = i
					i += 1
				kwargs['first_name'] = name[:j]
				kwargs['last_name'] = name[j:]
			
		for f in self.Fields:
			setattr( self, f, kwargs.get(f, None) )
		
		if self.date_of_birth is not None:
			self.date_of_birth = date_from_value( self.date_of_birth )
			if self.date_of_birth == invalid_date_of_birth:
				self.date_of_birth = None
		
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
			self.last_name = normalize_name( self.last_name )
			
		if self.first_name:
			self.first_name = normalize_name( self.first_name )
		
		if self.team:
			self.team = normalize_name( self.team )
		
		# Get the 3-digit nation code from the nation name.
		if self.nation:
			self.nation = unicode(self.nation).replace( u'&', u'and' ).strip()
			self.nation = countryTranslations.get(self.nation.upper(), self.nation)
			if not self.nation_code:
				nationKey = self.nation.upper()
				try:
					self.nation_code = uci_country_codes[nationKey]
				except KeyError:
					if nationKey in uci_country_codes_set:
						self.nation_code = nationKey
					else:
						raise KeyError( u'cannot find nation_code from nation: "{}" ({}, {})'.format(self.nation, self.last_name, self.first_name) )
		
		if self.nation_code:
			self.nation_code = self.nation_code.upper()
		
		if self.uci_code:
			self.uci_code = unicode(self.uci_code).upper().replace(u' ', u'')
			if len(self.uci_code) != 11:
				raise ValueError( u'uci_code has invalid length: {} ({}, {})'.format(self.uci_code, self.last_name, self.first_name) )

			if self.uci_code[:3] != self.uci_code[:3].upper():
				self.uci_code = self.uci_code[:3].upper + self.uci_code[3:]
				
			if self.uci_code[:3] not in uci_country_codes_set:
				raise ValueError( u'uci_code contains invalid nation code: {} ({}, {})'.format(self.uci_code, self.last_name, self.first_name) )
			
			if not self.date_of_birth:
				self.date_of_birth = datetime.date( int(self.uci_code[3:7]), int(self.uci_code[7:9]), int(self.uci_code[9:11]) )
				
			if not self.nation_code:
				self.nation_code = self.uci_code[:3]
			else:
				if self.nation_code != self.uci_code[:3]:
					raise KeyError( u'nation code does not match uci_code: {},{} ({}, {})'.format(self.nation_code, self.uci_code, self.last_name, self.first_name) )
		else:
			if self.nation_code and self.date_of_birth:
				self.uci_code = u'{}{}'.format( self.nation_code, self.date_of_birth.strftime('%Y%m%d') )
			
		if self.date_of_birth and not self.age:
			self.age = datetime.date.today().year - self.date_of_birth.year		# Competition age.
		
		if self.age is not None:
			try:
				self.age = int(self.age)
			except ValueError:
				raise ValueError( u'invalid age: {} ({}, {})'.format(self.age, self.last_name, self.first_name) )
				
		assert self.date_of_birth is None or isinstance(self.date_of_birth, datetime.date), 'invalid Date of Birth'
		
		self.cmp_policy = None
	
	def __repr__( self ):
		return '({})'.format( Utils.removeDiacritic( self.as_str(self.Fields) ) )
		
	def as_str( self, fields=None ):
		fields = fields or self.Fields
		data = [ unicode(getattr(self,f).upper() if f == 'last_name' else getattr(self,f)) for f in fields if getattr(self,f,None) is not None and f != 'row' ]
		for i in xrange(len(data)):
			d = data[i]
			for t, fmt in ((int, u'{}'), (float, u'{:.3f}')):
				try:
					d = fmt.format(t(d))
					break
				except ValueError:
					pass
			else:
				d = u'"{}"'.format( d )
			data[i] = d
			
		return u','.join( data )
		
	def as_list( self, fields=None ):
		lines = []
		fields = fields or self.Fields
		for f in fields:
			if f in self.KeyFields:
				v = getattr( self, f )
				if v is not None:
					if f == 'last_name':
						v = v.upper()
					lines.append( u'{}={}'.format(f, v) )
		for f in fields:
			if f not in self.KeyFields:
				v = getattr( self, f )
				if v is not None:
					if f == 'last_name':
						v = v.upper()
					lines.append( u'{}={}'.format(f, v) )
		return lines
	
	@property
	def full_name( self ):
		return u'{} {}'.format( self.first_name, self.last_name )
	
	def get_key( self ):
		if self.cmp_policy == self.ByPoints:
			return (-(self.points or 0), self.row)
		elif self.cmp_policy == self.ByPosition:
			return (self.position or sys.maxint, self.row)
		assert False, 'Invalid cmp_policy'
		
	def get_value( self ):
		if self.cmp_policy == self.ByPoints:
			return self.points
		elif self.cmp_policy == self.ByPosition:
			return self.position
		assert False, 'Invalid cmp_policy'

reAlpha = re.compile( '[^A-Z]+' )
header_sub = {
	u'RANK':			u'POSITION',
	u'POS':				u'POSITION',
	u'BIBNUM':			u'BIB',
	u'BIBNUMBER':		u'BIB',
	u'LICENSENUMBER':	u'LICENSE',
	u'DOB':				u'DATEOFBIRTH',
}
def scrub_header( h ):
	h = reAlpha.sub( '', Utils.removeDiacritic(unicode(h)).upper() )
	return header_sub.get(h, h)

class FindResult( object ):
	NoMatch, Success, SuccessSoundalike, MultiMatch = range(4)

	def __init__( self, search, matches, source, soundalike ):
		self.search = search
		self.matches = sorted(matches or [], key = lambda r: r.row)
		self.source = source
		self.soundalike = soundalike
		
	def get_key( self ):
		if len(self.matches) == 1:
			return self.matches[0].get_key()
		return (0, sys.maxint) if self.source.cmp_policy == Result.ByPoints else (sys.maxint, sys.maxint)
			
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
		return unicode(self.get_value())
		
	def get_message( self ):
		matchName = {
			self.Success:			_('Success'),
			self.SuccessSoundalike: _('Soundalike Match'),
			self.MultiMatch:		_('Multiple Matches'),
			self.NoMatch:			_('No Match'),
		}[self.get_status()]
		matches = u'\n'.join( u', '.join(r.as_list()) for r in self.matches )
		
		message = u'{matchName}: "{sheet_name}"\n\n{registration}:\n{registrationData}\n\n{matches}:\n{matchesData}'.format(
			matchName=matchName, sheet_name=self.source.sheet_name,
			registration=_('Registration'), registrationData=u', '.join(self.search.as_list()),
			matches=_('Matches'), matchesData=matches,
		)
		return message
		
def validate_uci_code( dCur, uci_code ):
	if not uci_code:
		raise ValueError( u'uci_code missing' )
	
	if len(uci_code) != 11:
		raise ValueError( u'uci_code is incorrect length ({}!=11): {}'.format( len(uci_code), uci_code ) )
	
	nation_code, year, month, day = uci_code[:3], uci_code[3:7], uci_code[7:9], uci_code[9:11]
	
	if nation_code not in uci_country_codes_set:
		raise ValueError( u'uci_code contains unknown nation {}'.format(uci_code) )
	
	try:
		year = int(year)
	except ValueError:
		raise ValueError( u'uci_code contains invalid year: {}'.format(uci_code) )
	try:
		month = int(month)
	except ValueError:
		raise ValueError( u'uci_code contains invalid month: {}'.format(uci_code) )		
	try:
		day = int(day)
	except ValueError:
		raise ValueError( u'uci_code contains invalid day: {}'.format(uci_code) )
	
	try:
		dob = datetime.date( year=year, month=month, day=day )
	except ValueError as e:
		raise ValueError( u'uci_code contains invalid date: {}: {}'.format(e, uci_code) )
	
	if dob > dCur:
		raise ValueError( u'uci_code is in the future: {}'.format(uci_code) )
	
	if dCur.year - dob.year < 3:
		raise ValueError( u'uci_code is too young: {}'.format(uci_code) )
	
	if dCur.year - dob.year > 110:
		raise ValueError( u'uci_code is too old: {}'.format(uci_code) )
		
class Source( object ):
	Indices = (
		'by_license', 'by_uci_code',
		'by_last_name', 'by_first_name',
		'by_mp_last_name', 'by_mp_first_name',
		'by_nation_code', 'by_date_of_birth', 'by_age',
	)
	def __init__( self, fname, sheet_name, soundalike=True, useUciCode=True, useLicense=True ):
		self.fname = fname
		self.sheet_name = sheet_name
		self.soundalike = soundalike
		self.useUciCode = useUciCode
		self.useLicense = useLicense
		self.results = []
		self.hasField = set()
		self.cmp_policy = None
		self.debug = False
		for i in self.Indices:
			setattr( self, i, {} )
		self._field_from_index = {}
	
	def empty( self ):
		return not self.results
	
	def field_from_index( self, i ):
		try:
			return self._field_from_index[i]
		except KeyError:
			self._field_from_index[i] = i[6:] if i.startswith('by_mp_') else i[3:]
			return self._field_from_index[i]
		
	def get_cmp_policy_field( self ):
		if self.cmp_policy == Result.ByPoints:
			return 'points'
		elif self.cmp_policy == Result.ByPosition:
			return 'position'
		else:
			return None
		
	def read( self, reader ):
		header_fields = ['name'] + list(Result.Fields)
		dCur = datetime.date.today()
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
				errors.append( u'{} - row {} - {}'.format(self.sheet_name, row_number+1, e) )
				traceback.print_exc()
				continue
			
			result.row_number = row_number
			
			if 'uci_code' in header_map:
				try:
					validate_uci_code( dCur, result.uci_code )
				except Exception as e:
					errors.append( u'{} - row {} - Warning: {} ({}, {})'.format(self.sheet_name, row_number+1, e, result.last_name, result.first_name) )
		
			if 'license' in header_map:
				if not result.license:
					errors.append( u'{} - row {} - Warning: {} ({}, {})'.format(self.sheet_name, row_number+1, u'missing license', result.last_name, result.first_name) )
		
			self.add( result )
		
		self.cmp_policy = Result.ByPoints if 'points' in self.hasField else Result.ByPosition
		for r in self.results:
			r.cmp_policy = self.cmp_policy
		
		return errors
	
	def get_ordered_fields( self ):
		return tuple(f for f in Result.Fields if f in self.hasField and f not in ('points', 'position', 'row'))
	
	def randomize_positions( self ):
		positions = range( 1, len(self.results)+1 )
		random.seed( 0xededed )
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
				for mp in doublemetaphone(v.replace('-','').encode('utf8')):
					if mp:
						try:
							idx[mp].append( result )
						except KeyError:
							idx[mp] = [result]
			else:								# Initialize a regular field index.
				assert idx_name != 'by_license' or v not in idx, 'Duplicate license: {}'.format(v)
				try:
					key = normalize_name_lookup(v)
				except:
					key = v					
				try:
					idx[key].append( result )
				except KeyError:
					idx[key] = [result]
	
	def get_match_fields( self, source ):
		indices = (
			('by_license',),
			('by_last_name', 'by_first_name', 'by_uci_code', ),
			('by_last_name', 'by_first_name', 'by_nation_code', 'by_age', ),
			('by_first_name', 'by_uci_code', ),
			('by_last_name', 'by_first_name',),
		)
		for pi in indices:
			if all( (self.field_from_index(i) in self.hasField) and (self.field_from_index(i) in source.hasField) for i in pi ):
				return tuple( self.field_from_index(i) for i in pi )
		return []
		
	def has_all_index_fields( self, search, indices ):
		return all( self.field_from_index(i) in self.hasField and getattr(search, self.field_from_index(i), None) is not None for i in indices )
			
	def match_indices( self, search, indices ):
		# Look for a set intersection of one element between all source criteria.
		
		if self.debug: print 'match_indices: searchKeys=', indices
		
		soundalike = False
		setCur = None
		for idx_name in indices:
			if self.debug: print "match_indices: matching on key:", idx_name
			idx = getattr( self, idx_name )
			v = getattr( search, self.field_from_index(idx_name), None )
			if not v or not idx:
				setCur = None
				if self.debug: print 'match_indices: missing attribute'
				break

			try:
				v = normalize_name_lookup( v )
			except:
				pass
				
			if self.debug: print 'match_indices: value=', v
			
			found = set()
			if idx_name.startswith( 'by_mp_' ):
				soundalike = True
				for mp in doublemetaphone(v.replace('-','').encode('utf8')):
					if mp and mp in idx:
						found |= set(idx[mp])
			elif v in idx:
				found = set(idx[v])
			
			if setCur is None:
				setCur = set(found)
			else:
				setCur &= set(found)
			
			if not setCur:
				if self.debug: print "match_indices: match failed. found=", found
				break
			
			if self.debug: print "matched:", setCur
		
		return FindResult( search, setCur, self, soundalike )
	
	def find( self, search ):
		''' Returns (result, messages) - result will be None if no match. '''
		if self.debug:
			print '-' * 60
			print 'sheet_name:', self.sheet_name
			print 'find: search=', search, hasattr( search, 'last_name'), hasattr( search, 'uci_code' ), getattr( search, 'uci_code' )
			print self.by_last_name.get('BELHUMEUR', None)
			print self.by_first_name.get('FELIX', None)

		# First check for a common License field.  If so, attempt to match it exactly and stop.
		if self.useLicense:
			pi = ['by_license']
			if self.has_all_index_fields(search, pi):
				return self.match_indices( search, pi )
		
		# If no license code, try find a perfect, unique match based on the following fields.
		if self.useUciCode:
			perfectIndices = (
				('by_last_name', 'by_first_name', 'by_uci_code', ),
				('by_last_name', 'by_first_name', 'by_nation_code', 'by_age', ),
			)
			for pi in perfectIndices:
				if self.has_all_index_fields(search, pi):
					if self.debug: print 'found index:', pi
					findResult = self.match_indices( search, pi )
					if findResult.get_status() == FindResult.Success:
						return findResult
			
		# Fail-over: try to find a sound-alike on the following combinations.
		indices = []
		if self.soundalike and self.useUciCode:
			potentialIndices = (
				('by_mp_last_name', 'by_mp_first_name', 'by_uci_code', ),
				('by_mp_last_name', 'by_mp_first_name', 'by_nation_code', 'by_age',),
				('by_mp_last_name', 'by_nation_code', 'by_age',),
			)
			
			for pi in potentialIndices:
				if self.has_all_index_fields(search, pi):
					if self.debug: print 'found index:', pi
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
			if self.has_all_index_fields(search, pi):
				if self.debug: print 'matching on fields:', pi
				findResult = self.match_indices( search, pi )
				if findResult.get_status() != findResult.NoMatch:
					if self.debug: print 'success', findResult
					return findResult
		
		return FindResult( search, [], self, False )
	
class ResultCollection( object ):
	def __init__( self ):
		self.sources = []
		
	def add_source( self, source ):
		self.sources.append( source )
		
if __name__ == '__main__':
	s = Source( 'CallupTest.xlsx', '2014 Result' )
	errors = s.read( GetExcelReader(self.fname) )
	print s.by_mp_last_name
	sys.exit()
	
	#for r in s.results:
	#	print r
	for k, v in sorted( ((k, v) for k, v in s.by_mp_last_name.iteritems()), key=lambda x: x[0] ):
		print '{}: {}'.format(k, ', '.join( Utils.removeDiacritic(r.full_name) for r in v ))
	for k, v in sorted( ((k, v) for k, v in s.by_mp_first_name.iteritems()), key=lambda x: x[0] ):
		print '{}: {}'.format(k, ', '.join( Utils.removeDiacritic(r.full_name) for r in v ))
		
	for r in s.results:
		for p_last in doublemetaphone(r.last_name.replace('-','').encode('utf8')):
			if not p_last:
				continue
			p_last_set = s.by_mp_last_name[p_last]
			for p_first in doublemetaphone(r.first_name.replace('-','').encode('utf8')):
				p_first_set = s.by_mp_first_name[p_first]
				p_last_first_set = p_last_set & p_first_set
				if len(p_last_first_set) > 1:
					print ', '.join( u'({}, {}, {})'.format(
							Utils.removeDiacritic(rr.full_name), Utils.removeDiacritic(rr.nation_code), rr.age,
						)
						for rr in p_last_first_set )

