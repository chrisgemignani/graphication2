
import math
from graphication.color import hex_to_rgba
from graphication import css, default_css

class Doughnut(object):
	
	def __init__(self, series_set, style=None):
		
		"""
		Constructor; creates a new WaveGraph.
		
		@param series_set: The data to plot, as a SeriesSet
		@type series_set: graphication.series.SeriesSet
		
		@param style: The Style to apply to this graph
		@type style: graphication.style.Style
		"""
		
		self.series_set = series_set
		
		self.style = default_css.merge(style)
	
	
	def set_size(self, width, height):
		self.width = width
		self.height = height
		
		self.center_x = width / 2.0
		self.center_y = height / 2.0
	
	
	def get_arc_point(self, radius, angle):
		x = math.cos(angle) * radius + self.center_x
		y = math.sin(angle) * radius + self.center_y
		return x, y
	
	
	def render(self, context, debug=False):
		
		context.save()
		
		graph_style = self.style['doughnut']
		outer_radius = self.center_x * graph_style.get_align('radius-outer', 1.0)
		inner_radius = self.center_x * graph_style.get_align('radius-inner', 0.5)
		
		# Work out the ratios of each series
		total = self.series_set.sum()
		
		current_angle = -(math.pi / 2.0) + (2*math.pi) * graph_style.get_align('circle-start', 1.0)
		angle_step = ((2*math.pi) / total) * graph_style.get_align('circle-length', 1.0)
		
		for series in self.series_set:
			new_angle = series.sum() * angle_step + current_angle
			context.move_to(*self.get_arc_point(outer_radius, current_angle))
			context.arc(self.center_x, self.center_y, outer_radius, current_angle, new_angle)
			context.line_to(*self.get_arc_point(inner_radius, new_angle))
			context.arc_negative(self.center_x, self.center_y, inner_radius, new_angle, current_angle)
			context.close_path()
			context.set_source_rgba(*series.color_as_rgba())
			context.fill()
			current_angle = new_angle
		
		context.restore()