
import os
import sys
import xlwt
import datetime
import Utils
from Model import Source
from Excel import GetExcelReader

RegistrationSheet = 'Registration'

def make_title( field ):
	return (field[:1].upper + field[1:]).replace( '_', '' )

def GetCallups( fname, soundalike=True ):
	reader = GetExcelReader( fname )
	
	registration_sheet_count = sum( 1 for sheet in reader.sheet_names() if sheet == RegistrationSheet )
	if registration_sheet_count == 0:
		raise ValueError, 'Spreadsheet is missing "{}" sheet'.format( RegistrationSheet )
	if registration_sheet_count > 1:
		raise ValueError, 'Spreadsheet must have exactly one sheet named "{}"'.format( RegistrationSheet )
		
	registration = Source( fname, RegistrationSheet, False )
	errors = registration.read()
	
	sources = []
	for sheet in reader.sheet_names():
		if sheet == RegistrationSheet:
			continue
		source = Source( fname, sheet, soundalike )
		source.read()
		if not source.empty():
			sources.append( source )
	
	# Add a random sequence as a final sort order.
	registration.randomize_positions()
	sources.append( registration )
	
	for reg in registration.results:
		reg.result_vector = [source.find(reg) for source in sources]
	
	callup_order = sorted( registration.results, key = lambda reg: tuple(r.get_key() for r in reg.result_vector) )
	
	callup_results = []
	registration_headers = registration.get_ordered_fields()
	
	callup_headers = list(registration_headers) + [source.sheet_name for source in sources[:-1]]
	
	for reg in callup_order:
		row = [getattr(reg, f, u'') for f in registration_headers]
		row.extend( reg.result_vector[:-1] )
		callup_results.append( row )
		
	return registration_headers, callup_headers, callup_results, sources

def make_title( title ):
	return u' '.join( (w[:1].upper() + w[1:]).replace(u'Uci',u'UCI').replace('Of','of') for w in title.split(u'_') )

if __name__ == '__main__':
	fname = 'CallupTest.xlsx'
	registration_headers, callup_headers, callup_results, sources = GetCallups( fname )
	for row in callup_results:
		print [Utils.removeDiacritic(unicode(v)) for v in row]
	CallupResultsToExcel( fname, registration_headers, callup_headers, callup_results )
