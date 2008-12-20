
from graphication import default_css, Series
from graphication.text import text_bounds
from graphication.color import hex_to_rgba
from graphication.scales import SimpleScale, VerticalWavegraphScale, BaseScale

class LineGraph(object):
	
	def __init__(self, series_set, scale, style=None, vertical_scale=True, zero_base=True, smoothed=True, bottom_scale=False, no_bottom_labels=False, vertical_label="", peak_highlight=None, two_passes=False):
		
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
		self.no_bottom_labels = no_bottom_labels
		self.vertical_label = vertical_label
		self.peak_highlight = peak_highlight
		self.two_passes = two_passes
		self.first_pass = False
		
		self.calc_rel_points()
	
	
	def calc_rel_points(self):
		
		"""Calculates the relative shapes of the sections"""
		
		if isinstance(self.vertical_scale, BaseScale):
			self.y_scale = self.vertical_scale
		else:
			# Work out our extents
			y_min, y_max = self.series_set.value_range()
			if self.zero_base:
				y_min = 0
			self.y_scale = VerticalWavegraphScale(y_min, y_max)
	
	
	def set_size(self, width, height):
		self.width = width
		self.height = height
		self.calc_plot_height()
	
	
	def get_vertical_scale(self):
		return self.y_scale
	
	
	def calc_plot_height(self):
		
		# Are we ignoring the bottom labels?
		if self.no_bottom_labels:
			self.plot_height = self.height
			return
		
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
		if self.two_passes:
			self.first_pass = True
			self._render(context)
		self.first_pass = False
		self._render(context)
	
	def _render(self, context, debug=False):
		
		context.save()
		
		fascent, fdescent, fheight, fxadvance, fyadvance = context.font_extents()
		
		# Render the labels and lines
		if not self.first_pass:
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
				
				if title:
					x_bearing, y_bearing, width, height = context.text_extents(title)[:4]
					
					padding = label_style.get_float("padding")
					align = label_style.get_align("text-align")
					
					context.move_to(x - (align * width), self.plot_height + padding + fheight / 2.0 - fdescent)
					context.set_source_rgba(*label_style.get_color("color"))
					if not self.no_bottom_labels:
						context.show_text(title)
					context.fill()
				
				context.set_line_width(line_style.get_float("width", 1))
				context.set_source_rgba(*line_style.get_color("color", "#aaa"))
				context.move_to(x, 0)
				context.line_to(x, self.plot_height + line_style.get_float("padding", 0))
				context.stroke()
		
		# Draw the lines
		smooth = self.style['linegraph line'].get_float("smoothness", 0.5)
		y_size = self.style['linegraph'].get_align("height", 1)
		
		for series in self.series_set:
			
			# Get the line's points
			points = [(self.scale.get_point(x)*self.width, (1-(self.y_scale.get_point(y)*y_size))*self.plot_height) for x, y in series.items()]
			xs = [self.scale.get_value(self.scale.get_point(x)) for x,y in series.items()]
			
			# Get style infos
			line_style = self.style['linegraph line']
			if series.line_width:
				context.set_line_width(series.line_width)
			else:
				context.set_line_width(line_style.get_float("width", 2))
			context.set_source_rgba(*series.color_as_rgba())
			
			# Finish off a line stylishly
			def stroke(nx=None, ox=None):
				
				curve = context.copy_path()
				
				# If there's a peak highlight line, we need to draw it
				if self.peak_highlight:
					context.save()
					peak_height, colour = self.peak_highlight
					context.set_source_rgba(*hex_to_rgba(colour))
					# Now, use the curve as a mask for that
					context.line_to(nx, self.plot_height)
					context.line_to(ox, self.plot_height)
					context.clip()
					# Draw a rectangle at the right height for highlight
					bottom = (1 - self.y_scale.get_point(peak_height)) * self.plot_height
					context.rectangle(0, 0, self.width, bottom)
					context.fill()
					context.restore()
					context.append_path(curve)
				
				if prev_style == Series.STYLE_DASHED:
					context.set_source_rgba(*series.color_as_rgba())
					context.set_dash([3, 2], 2)
					context.stroke()
					context.set_dash([], 0)
				
				elif prev_style == Series.STYLE_LIGHT:
					r,g,b,a = series.color_as_rgba()
					context.set_source_rgba(r,g,b,a*0.5)
				
				elif prev_style == Series.STYLE_VLIGHT:
					r,g,b,a = series.color_as_rgba()
					context.set_source_rgba(r,g,b,a*0.4)
				
				elif prev_style in [Series.STYLE_LINETOP, Series.STYLE_DOUBLEFILL, Series.STYLE_WHOLEFILL]:
					r,g,b,a = series.color_as_rgba()
					if self.two_passes and self.first_pass:
						# Now fill in under the curve
						context.line_to(nx, self.plot_height)
						context.line_to(ox, self.plot_height)
						if series.fill_color:
							context.set_source_rgba(*series.fill_color_as_rgba())
						else:
							context.set_source_rgba(r,g,b,a*0.5)
						context.fill()
						
						if prev_style == Series.STYLE_DOUBLEFILL:
							# Now fill in over the curve
							context.append_path(curve)
							context.line_to(nx, 0)
							context.line_to(ox, 0)
							if series.fill_color:
								r,g,b,a = series.fill_color_as_rgba()
								context.set_source_rgba(r,g,b,a*0.4)
							else:
								context.set_source_rgba(r,g,b,a*0.20)
							context.fill()
						
						elif prev_style == Series.STYLE_WHOLEFILL:
							# Now fill in over the curve
							context.append_path(curve)
							context.line_to(nx, 0)
							context.line_to(ox, 0)
							if series.fill_color:
								r,g,b,a = series.fill_color_as_rgba()
								context.set_source_rgba(r,g,b,a)
							else:
								context.set_source_rgba(r,g,b,a*0.5)
							context.fill()
					
					context.append_path(curve)
					context.set_source_rgba(*series.color_as_rgba())
				
				else:
					context.set_source_rgba(*series.color_as_rgba())
				
				if self.first_pass:
					context.new_path()
					return
				
				context.stroke()
			
			# Draw the line
			prev_style = series.style_at(0)
			last_change = 0
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
				if draw_style != prev_style:
					stroke(nx, last_change)
					prev_style = draw_style
					context.move_to(*points[j])
					last_change = nx
			
			# Now close the line overall
			stroke(nx, last_change)
		
		context.restore()


class TooClose(Exception): pass
