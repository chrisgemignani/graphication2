
from graphication import default_css, Series
from graphication.text import text_bounds
from graphication.color import hex_to_rgba
from graphication.scales import SimpleScale, VerticalWavegraphScale

class Graph(object):
	
	
	def set_size(self, width, height):
		self.width = width
		self.height = height
		self.calc_plot_size()
	
	
	def calc_label_dimension(self, scale, is_height, major_selector, minor_selector):
		"""
		Calculates the maximum width/height of a scale's labels.
		"""
		
		major_style = self.style[major_selector]
		minor_style = self.style[minor_selector]
		
		# Work out the maxiumum label width
		max_size = 0
		for linepos, title, is_major in scale.get_lines():
			
			label_style = (is_major and major_style or minor_style).sub('label')
			
			width, height = text_bounds(
				title,
				label_style.get_float("font-size"), 
				label_style.get_font(),
				label_style.get_cairo_font_style(),
				label_style.get_cairo_font_weight(),
			)
			padding = label_style.get_float("padding")
			
			max_size = max(max_size, is_height and height or width + padding)
		return max_size