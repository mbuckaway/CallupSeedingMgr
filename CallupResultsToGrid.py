import wx
import wx.grid as gridlib
import sys
import Utils
import Model
from GetCallups import make_title

def CallupResultsToGrid( grid, registration_headers, callup_headers, callup_results, is_callup=True, top_riders=sys.maxint, exclude_unranked=False ):
	callup_results = callup_results[:top_riders]
	if exclude_unranked:
		callup_results = [r for r in callup_results if any(r[k] for k in xrange(len(registration_headers), len(callup_headers)))]
	
	if not is_callup:
		callup_results = list(reversed(callup_results))
	
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
	
	grid.DeleteCols( 0, grid.GetNumberCols() )
	Utils.AdjustGridSize( grid, rowsRequired=len(callup_results), colsRequired=len(callup_headers) - len(ignore_headers) + 1 )
	
	for ih, v in enumerate(callup_headers):
		if v in ignore_headers:
			continue
		col = header_col[v]
		
		attr = gridlib.GridCellAttr()
		attr.SetReadOnly()
		if v in Model.Result.NumericFields or ih >= len(registration_headers):
			attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTRE )
		grid.SetColAttr( col, attr )
		
		grid.SetColLabelValue( col, make_title(v) )
		
	# Set an empty column so we can track the row if the user switches things around manually.
	attr = gridlib.GridCellAttr()
	attr.SetReadOnly()
	attr.SetTextColour( wx.WHITE )
	grid.SetColAttr( grid.GetNumberCols()-1, attr )
	grid.SetColLabelValue( grid.GetNumberCols()-1, u'' )
	
	successSoundalikeColour = wx.Colour(255, 255, 0)
	multiMatchColour = wx.Colour(255,140,0)
	
	len_callup_results = len(callup_results)
	for row, result in enumerate(callup_results):
		for c, v in enumerate(result):
			if callup_headers[c] in ignore_headers:
				continue
			
			col = header_col[callup_headers[c]]
			
			colour = wx.WHITE
			try:
				s = v.get_status()
				if s == v.SuccessSoundalike:
					colour = successSoundalikeColour
				elif s == v.MultiMatch:
					colour = multiMatchColour
			except AttributeError as e:
				pass
			grid.SetCellBackgroundColour( row, col, colour )
			
			try:
				v = v.get_value()
			except AttributeError:
				pass
			
			if v is None:
				grid.SetCellValue( row, col, u'' )
				continue
				
			try:
				grid.SetCellValue( row, col, u'{:g}'.format(v) )
			except ValueError:
				grid.SetCellValue( row, col, unicode(v).upper() if c == last_name_col else unicode(v) )
		
		# Record the row index in a hidden column so we can recover the original results.
		grid.SetCellValue( row, grid.GetNumberCols()-1, unicode(row if is_callup else len_callup_results - row - 1) )
	
	if not is_callup:
		for row in xrange(grid.GetNumberRows()):
			grid.SetRowLabelValue( row, unicode(grid.GetNumberRows() - row) )
	
	grid.AutoSize()
	grid.SetColSize( grid.GetNumberCols()-1, 0 )
