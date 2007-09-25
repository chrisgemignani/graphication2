
from graphication import default_css


class Colourer(object):
	
	"""A colourer takes a SeriesSet and colours the
	series in nicely to be shown in a wavegraph."""
	
	
	def __init__(self, style=None):
		
		self.style = default_css.merge(style)
	
	
	def colour(self, series_set):
		
		colours = ["537dcc", "7c9cd7", "668ed2", "527ccb", "7ba0d4", "507fcf"]
		for series in series_set:
			series.color = colours[0]
			colours = colours[1:] + colours[:1]