

class Style(object):
	
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
				"vertical_extent": 0.9,
				"smoothness": 0.25,
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