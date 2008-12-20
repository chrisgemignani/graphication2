
import sys

from graphication import default_css, Series
from graphication.text import text_bounds
from graphication.color import hex_to_rgba
from graphication.scales import SimpleScale, VerticalWavegraphScale
from graphication.graph import Graph

class BarChart(Graph):
	
	def __init__(self, series_set, scale, style=None, vertical_scale=True, stacked=True, zero_base=True):
		
		"""
		Constructor; creates a new LineGraph.
		
		@param mseries: The data to plot, as a MultiSeries
		@type mseries: graphication.series.MultiSeries
		
		@param style: The Style to apply to this graph
		@type style: graphication.style.Style
		
		@param scale: The Scale to use for the graph.
		@type scale: graphication.scales.BaseScale
		
		@param smoothed: If the graph is smoothed (not straight lines)
		@type smoothed: bool
		"""
		
		self.series_set = series_set
		self.style = default_css.merge(style)
		self.scale = scale
		self.stacked = stacked
		self.zero_base = zero_base
		self.vertical_scale = vertical_scale
		
		# Initialise the vertical scale
		if stacked:
			y_min, y_max = self.stacked_value_range()
		else:
			y_min, y_max = self.series_set.value_range()
		if self.zero_base:
			y_min = 0
		self.y_scale = VerticalWavegraphScale(y_min, y_max)
	
	
	def stacked_value_range(self):
		y_min, y_max = sys.maxint, 0
		print self.series_set, self.series_set.series
		for series in self.series_set:
			s_min, s_max = series.value_range()
			y_min = min(s_min, y_min)
			y_max += s_max
		if not self.zero_base:
			y_max -= y_min
		print y_min, y_max
		return y_min, y_max
	
	
	def calc_plot_size(self):
		self.plot_height = self.height - self.calc_label_dimension(
			self.scale,
			is_height = True,
			major_selector = "barchart grid#x.major",
			minor_selector = "barchart grid#x.minor",
		)
		self.plot_width = self.width
		self.plot_left = 0
		self.plot_top = 0
	
	
	def render(self, context, debug=False):
		
		context.save()
		
		### Draw the bars
		# Get width per bar block
		keys = self.series_set.keys()
		per_bar = self.plot_width / len(keys)
		# Some more drawing parameters
		zero_line = self.plot_top + self.plot_height
		bar_style = self.style["barchart bar"]
		bar_padding = bar_style.get_float("padding")
		bar_padding_top = bar_style.get_float("padding-top")
		border_width = bar_style.get_float("border-width")
		border_color = bar_style.get_color("border-color")
		# Draw the bars at each location
		left = self.plot_left
		for key in keys:
			stack = self.series_set.stack(key)
			bottom = zero_line
			inner_left = 0
			for series, value in stack:
				height = 0 - self.y_scale.get_point(value) * self.plot_height
				if self.stacked:
					x, y, w, h = (
						left + bar_padding,
						bottom,
						per_bar - bar_padding*2,
						height + bar_padding_top,
					)
				else:
					x, y, w, h = (
						left + inner_left + bar_padding,
						bottom,
						per_bar / len(stack) - bar_padding*2,
						height + bar_padding_top,
					)
					inner_left += per_bar / len(stack)
				context.rectangle(x, y, w, h)
				context.set_source_rgba(*series.color_as_rgba())
				context.fill()
				# Draw outer border if needed
				if border_width:
					context.rectangle(
						x + 0.5,
						y - 0.5,
						w - 1,
						h + 1,
					)
					context.set_source_rgba(*border_color)
					context.stroke()
				if self.stacked:
					bottom += height
			
			# TODO: See if we need to draw a label here, too
			
			
			left += per_bar
		
		context.restore()

class TooClose(Exception): pass
