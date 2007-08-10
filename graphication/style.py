

class Style(object):
	
	"""
	A Style determines how a graph is drawn.
	Options can be specific (e.g. to a graph or output type). If a specific
	option is asked for and it doesn't exist, the 'default' dict will be
	searched as a fallback.
	"""
	
	def __init__(self):
		
		self.styles = {
			"default": {
				"grid_minor_color": "#ccc",
				"grid_minor_width": 1,
				"grid_major_color": "#aaa",
				"grid_major_width": 2,
				"label_color": "#999",
				"label_size": 15,
				"label_font": "Sans",
			},
			"png": {
				"background": "#ffff",
			},
			"wavegraph": {
				"curve_label_color": "#fff",
				"vertical_extent": 0.9,        # How much of the vertical space the highest peak occupies
				"vertical_center": 0.5,        # The vertical center; 1 turns it into a histogram
				"smoothness": 0.3,             # From 0 - 1, how 'smooth' the curves are.
			},
		}
	
	
	def __getitem__(self, key):
		
		try:
			type, key = key.split(":")
		except (TypeError, ValueError):
			type = "default"
		
		if type in self.styles:
			if key in self.styles[type]:
				return self.styles[type][key]
		return self.styles['default'][key]
	
	
	def __setitem__(self, key, value):
		
		try:
			type, key = key.split(":")
		except (TypeError, ValueError):
			type = "default"
		
		if type not in self.styles:
			self.styles[type] = {}
		
		self.styles[type][key] = value