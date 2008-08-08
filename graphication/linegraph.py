
from graphication import default_css, Series
from graphication.text import text_bounds
from graphication.color import hex_to_rgba
from graphication.scales import SimpleScale, VerticalWavegraphScale

class LineGraph(object):
	
	def __init__(self, series_set, scale, style=None, vertical_scale=True, zero_base=True, smoothed=True):
		
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
		self.zero_base = zero_base
		self.vertical_scale = vertical_scale
		self.smoothed = smoothed
		
		self.calc_rel_points()
	
	
	def calc_rel_points(self):
		
		"""Calculates the relative shapes of the sections"""
		
		# Get the style stuff
		
		# Work out our extents
		y_min, y_max = self.series_set.value_range()
		if self.zero_base:
			y_min = 0
		self.y_scale = VerticalWavegraphScale(y_min, y_max)
	
	
	def set_size(self, width, height):
		self.width = width
		self.height = height
		self.calc_plot_height()
	
	
	def calc_plot_height(self):
		
		major_style = self.style['linegraph grid.major']
		minor_style = self.style['linegraph grid.minor']
		
		# Work out the maxiumum label width
		max_height = 0
		for linepos, title, ismajor in self.scale.get_lines():
			
			if ismajor:
				this_style = major_style
			else:
				this_style = minor_style
			
			label_style = this_style.sub('label')
			
			width, height = text_bounds(
				title,
				label_style.get_float("font-size"), 
				label_style.get_font(),
				label_style.get_cairo_font_style(),
				label_style.get_cairo_font_weight(),
			)
			padding = label_style.get_float("padding")
			
			max_height = max(max_height, height + padding)
		self.plot_height = self.height - max_height
	
	
	def render(self, context, debug=False):
		
		context.save()
		
		# Draw the vertical scale, if necessary
		if self.vertical_scale:
			major_style = self.style['linegraph grid#y.major']
			minor_style = self.style['linegraph grid#y.minor']
			
			for linepos, title, ismajor in self.y_scale.get_lines():
			
				if ismajor:
					this_style = major_style
				else:
					this_style = minor_style
				
				line_style = this_style.sub('line')
				label_style = this_style.sub('label')
				
				context.select_font_face(
					label_style.get_font(),
					label_style.get_cairo_font_style(),
					label_style.get_cairo_font_weight(),
				)
				context.set_font_size( label_style.get_float("font-size") )
				
				y = linepos * self.plot_height
				
				fascent, fdescent, fheight, fxadvance, fyadvance = context.font_extents()
				x_bearing, y_bearing, width, height = context.text_extents(title)[:4]
				
				padding = label_style.get_float("padding")
				align = label_style.get_align("text-align")
				
				context.move_to(0 - padding - (align * width), y + fheight / 2.0 - fdescent)
				context.set_source_rgba(*label_style.get_color("color"))
				context.show_text(title)
				
				context.set_line_width(line_style.get_float("width", 1))
				context.set_source_rgba(*line_style.get_color("color", "#aaa"))
				
				context.move_to(0 - line_style.get_float("padding", 0), y)
				context.line_to(self.width, y)
				context.stroke()
		
		# Render the labels and lines
		
		major_style = self.style['linegraph grid#x.major']
		minor_style = self.style['linegraph grid#x.minor']
		
		for linepos, title, ismajor in self.scale.get_lines():
			
			if ismajor:
				this_style = major_style
			else:
				this_style = minor_style
			
			line_style = this_style.sub('line')
			label_style = this_style.sub('label')
			
			context.select_font_face(
				label_style.get_font(),
				label_style.get_cairo_font_style(),
				label_style.get_cairo_font_weight(),
			)
			context.set_font_size( label_style.get_float("font-size") )
			
			x = linepos * self.width
			
			fascent, fdescent, fheight, fxadvance, fyadvance = context.font_extents()
			x_bearing, y_bearing, width, height = context.text_extents(title)[:4]
			
			padding = label_style.get_float("padding")
			align = label_style.get_align("text-align")
			
			context.move_to(x - (align * width), self.plot_height + padding + fheight / 2.0 - fdescent)
			context.set_source_rgba(*label_style.get_color("color"))
			context.show_text(title)
			context.fill()
			
			context.set_line_width(line_style.get_float("width", 1))
			context.set_source_rgba(*line_style.get_color("color", "#aaa"))
			context.move_to(x, 0)
			context.line_to(x, self.plot_height + line_style.get_float("padding", 0))
			context.stroke()
			
		
		# Draw the lines
		smooth = self.style['linegraph line'].get_float("smoothness", 0.5)
		y_size = self.style['linegraph'].get_align("height", 0.9)
		
		for series in self.series_set:
			
			# Get the line's points
			points = [(self.scale.get_point(x)*self.width, (1-(self.y_scale.get_point(y)*y_size))*self.plot_height) for x, y in series.items()]
			xs = [self.scale.get_value(self.scale.get_point(x)) for x,y in series.items()]
			
			# Get style infos
			line_style = self.style['linegraph line']
			context.set_line_width(line_style.get_float("width", 2))
			context.set_source_rgba(*series.color_as_rgba())
			
			# Finish off a line stylishly
			def stroke():
				if prev_style == Series.STYLE_DASHED:
					
					r,g,b,a = series.color_as_rgba()
					
					import cairo
					linear = cairo.LinearGradient(0, 0, self.width, self.height)
					for i in range(0, self.width, 5):
						dt = 1.5 / float(self.width)
						mid = i / float(self.width)
						linear.add_color_stop_rgba(mid-dt,  r,g,b,a*0.34)
						linear.add_color_stop_rgba(mid-(dt-0.001), r,g,b,a*0.8)
						linear.add_color_stop_rgba(mid+(dt-0.001), r,g,b,a*0.8)
						linear.add_color_stop_rgba(mid+dt, r,g,b,a*0.34)
					context.set_source(linear)
				
				elif prev_style == Series.STYLE_LIGHT:
					r,g,b,a = series.color_as_rgba()
					context.set_source_rgba(r,g,b,a*0.5)
				
				elif prev_style == Series.STYLE_VLIGHT:
					r,g,b,a = series.color_as_rgba()
					context.set_source_rgba(r,g,b,a*0.4)
				
				else:
					context.set_source_rgba(*series.color_as_rgba())
				
				context.stroke()
			
			# Draw the line
			prev_style = series.style_at(0)
			context.move_to(*points[0])
			for j in range(1, len(points)):
				# Get the drawstyle for this coord
				draw_style = series.style_at(xs[j])
				
				ox, oy = points[j-1]
				nx, ny = points[j]
				
				dx = (nx - ox) * smooth
				if self.smoothed:
					context.curve_to(ox+dx, oy, nx-dx, ny, nx, ny)
				else:
					context.line_to(nx, ny)
				
				# If we have a new draw style, we need to end this segment and begin another
				if prev_style and draw_style != prev_style:
					stroke()
					prev_style = draw_style
					context.move_to(*points[j])
			
			# Now close the line overall
			stroke()
		
		context.restore()


class TooClose(Exception): pass
