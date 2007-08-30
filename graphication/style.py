

class Style(object):
	
	"""
	A Style determines how a graph is drawn.
	Options can be specific (e.g. to a graph or output type). If a specific
	option is asked for and it doesn't exist, the 'default' dict will be
	searched as a fallback.
	There is also inheritance; if curve_label_color isn't found, then it will
	look for label_color and then color. This happens before falling back to
	the default style.
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
				"font": "Sans",
				"font_weight": "normal",
				"debug": False,
				"align": "center",
				"point_radius": 7,
				"link_width": 2,
				"link_color": "#600",
				"label_padding": 10,
			},
			"label": {
				"vertical_extent": 1.0,
			},
			"png": {
				"background": "#ffff",
			},
			"wavegraph": {
				"curve_label_color": "#fff",
				"vertical_extent": 0.9,        # How much of the vertical space the highest peak occupies
				"vertical_center": 0.5,        # The vertical center; 1 turns it into a histogram
				"smoothness": 0.3,             # From 0 - 1, how 'smooth' the curves are.
				"label_accuracy": 5,           # The higher it is, the better the on-curve labels fit (and the longer to render)
				"curve_label_maxcount": 10,    # The maximum number of labels on any given curve
				"curve_label_spacing": 200,    # The minimum amount of space between on-curve labels
				"dimming_top": 0,              # The on-label size below which labels are make more transparent
				"dimming_bottom": 0,           # The on-label size at which labels are completely dimmed/invisible
			},
		}
	
	
	def get_levels(self, key):
		"""Splits a key into its various inheritance levels."""
		parts = key.split("_")
		for i in range(len(parts), 0, -1):
			yield "_".join(parts[-i:])
	
	
	def __getitem__(self, key):
		
		try:
			type, key = key.split(":")
		except (TypeError, ValueError):
			type = "default"
		
		if type in self.styles:
			for subkey in self.get_levels(key):
				if subkey in self.styles[type]:
					return self.styles[type][subkey]
		if type == "default":
			raise ValueError("'%s' was not found, nor does it have an inherited value." % key)
		else:
			return self[key]
	
	
	def __setitem__(self, key, value):
		
		try:
			type, key = key.split(":")
		except (TypeError, ValueError):
			type = "default"
		
		if type not in self.styles:
			self.styles[type] = {}
		
		self.styles[type][key] = value