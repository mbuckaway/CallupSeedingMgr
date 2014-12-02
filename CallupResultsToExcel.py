import wx
import sys
import datetime
import xlsxwriter
import Utils
import Model
from FitSheetWrapper import FitSheetWrapper
from GetCallups import make_title

def CallupResultsToExcel( fname_excel, registration_headers, callup_headers, callup_results, is_callup=True, top_riders=sys.maxint, exclude_unranked=False ):
	callup_results = callup_results[:top_riders]
	if exclude_unranked:
		callup_results = [r for r in callup_results if any(r[k] for k in xrange(len(registration_headers), len(callup_headers)))]
	
	if not is_callup:
		callup_results = reversed( callup_results )
	

	wb = xlsxwriter.Workbook( fname_excel )
	ws = wb.add_worksheet('Callups' if is_callup is True else 'Seeding')
	fit_sheet = FitSheetWrapper( ws )
	
	bold_format = wb.add_format( {'bold': True} )
	date_format = wb.add_format( {'num_format': 'yyyy/mm/dd'} )
	
	rowNum = 0
	last_name_col = None
	ignore_headers = set(['age'])
	for col, v in enumerate(callup_headers):
		if v == 'last_name':
			last_name_col = col
		if v == 'uci_code':
			ignore_headers.add( 'date_of_birth' )
			ignore_headers.add( 'nation_code' )
			
	header_col = {}
	col_cur = 0
	for v in callup_headers:
		if v in ignore_headers:
			continue
		header_col[v] = col_cur
		col_cur += 1
			
	for v in callup_headers:
		if v in ignore_headers:
			continue
		fit_sheet.write( rowNum, header_col[v], make_title(v), bold_format, bold=True )
	rowNum += 1
		
	for row in callup_results:
		for c, v in enumerate(row):
			if callup_headers[c] in ignore_headers:
				continue
			
			try:
				v = v.get_value()
			except AttributeError:
				pass
			
			col = header_col[callup_headers[c]]
			if isinstance(v, datetime.date):
				fit_sheet.write( rowNum, col, v, date_format )
			else:
				fit_sheet.write( rowNum, col, unicode(v).upper() if c == last_name_col else v )
		rowNum += 1
	
	wb.close()

