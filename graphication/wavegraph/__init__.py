
from graphication import default_css
from graphication.text import text_bounds
from graphication.color import hex_to_rgba
from graphication.scales import SimpleScale

class WaveGraph(object):
	
	def __init__(self, series_set, scale, style=None, label_curves=False, vertical_axis=False):
		
		"""
		Constructor; creates a new WaveGraph.
		
		@param mseries: The data to plot, as a MultiSeries
		@type mseries: graphication.series.MultiSeries
		
		@param style: The Style to apply to this graph
		@type style: graphication.style.Style
		
		@param scale: The Scale to use for the graph.
		@type scale: graphication.scales.BaseScale
		
		@param label_curves: If the curves should have labels written directly on top of them, fitted into their shape. Note: Takes a while to render.
		@type label_curves: bool
		
		@param vertical_axis: If a vertical scale should be drawn on the graph
		@type vertical_axis: bool
		"""
		
		self.series_set = series_set
		self.style = style
		self.scale = scale
		
		self.calc_rel_points()
	
	
	def calc_rel_points(self):
		
		"""Calculates the relative shapes of the sections"""
		
		# Get the style stuff
		y_offset = self.style['wavegraph'].get_align("vertical-align", 0.5)
		y_size = self.style['wavegraph'].get_align("height", 0.9)
		
		# Work out our extents
		y_total = max([total for (key, total) in self.series_set.totals()])
		y_scale = SimpleScale(0, y_total)
		
		# Calculate the points
		cols = []
		self.xs = []
		
		for x, stack in self.series_set.stacks():
			self.xs.append(self.scale.get_point(x))
			
			# Collect the points
			ys = []
			total = 0
			for ser, val in stack:
				y = y_scale.get_point(val) * y_size
				ys.append(total)
				total += y
			ys.append(total)
			shift = 1 - total
			
			# Shift them down to center them
			ys = map(lambda a: a + (shift * y_offset), ys)
			
			cols.append(ys)
		
		self.rows = zip(*cols)
	
	
	def set_size(self, width, height):
		self.width = width
		self.height = height
	
	
	def render(self, context, debug=False):
		
		context.save()
		
		major_style = self.style['wavegraph grid.major']
		minor_style = self.style['wavegraph grid.minor']
		
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
			
			max_height = max(max_height, height + padding*2)
		
		plot_height = self.height - max_height
		
		# Render the labels and lines
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
			
			x_bearing, y_bearing, width, height = context.text_extents(title)[:4]
			
			padding = label_style.get_float("padding")
			align = label_style.get_align("text-align")
			
			context.move_to(x - (align * width), plot_height + padding + height / 2.0)
			context.set_source_rgba(*label_style.get_color("color"))
			context.show_text(title)
			
			context.set_line_width(line_style.get_float("width"))
			context.set_source_rgba(*line_style.get_color("color"))
			x = linepos * self.width
			context.move_to(x, 0)
			context.line_to(x, plot_height)
			context.stroke()
		
		
		# Draw the strips
		smooth = self.style['wavegraph curve'].get_float("smoothness")
		points = [[(x*self.width, y*plot_height) for x, y in zip(self.xs, ys)] for ys in self.rows]
		
		i = -1
		for series in self.series_set:
			i += 1
			
			# Get the two lists of points
			tops = points[i]
			bottoms = points[i+1]
			
			# Draw the tops
			context.move_to(*tops[0])
			for j in range(1, len(tops)):
				ox, oy = tops[j-1]
				nx, ny = tops[j]
				dx = (nx - ox) * smooth
				context.curve_to(ox+dx, oy, nx-dx, ny, nx, ny)
			
			# And the bottoms
			context.line_to(*bottoms[-1])
			for j in range(2, len(bottoms)+1):
				ox, oy = bottoms[-(j-1)]
				nx, ny = bottoms[-j]
				dx = (nx - ox) * smooth
				context.curve_to(ox+dx, oy, nx-dx, ny, nx, ny)
			
			# Close and fill
			context.set_source_rgba(*series.color_as_rgba())
			context.close_path()
			context.fill()
		
		
		# Do we need labels on the bottom?
		#if self.x_labels_major:
			#context.save()
			#context.translate(0, self.cheight)
			#self.x_labels_major.render(context,
				#color=self.style['wavegraph:label_color'],
				#size=self.style['wavegraph:label_size'],
				#font=self.style['wavegraph:label_font'],
			#)
			#context.restore()
		
		## Render the curve labels if needed
		#if self.curve_labels:
			#if self.style['wavegraph:debug']:
				#self.curve_labels.render_debug(context)
			#self.curve_labels.render(context,
				#color=self.style['wavegraph:curve_label_color'],
				#font=self.style['wavegraph:curve_label_font'],
				#weight=self.style['wavegraph:curve_label_font_weight'],
				#dimming_top=self.style['wavegraph:dimming_top'],
				#dimming_bottom=self.style['wavegraph:dimming_bottom'],
			#)
		
		context.restore()