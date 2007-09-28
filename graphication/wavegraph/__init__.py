
from graphication import default_css
from graphication.text import text_bounds
from graphication.color import hex_to_rgba
from graphication.scales import SimpleScale, VerticalWavegraphScale

class WaveGraph(object):
	
	def __init__(self, series_set, scale, style=None, label_curves=True, vertical_scale=False):
		
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
		self.style = default_css.merge(style)
		self.scale = scale
		self.label_curves = label_curves
		self.vertical_scale = vertical_scale
		
		self.calc_rel_points()
	
	
	def calc_rel_points(self):
		
		"""Calculates the relative shapes of the sections"""
		
		# Get the style stuff
		y_offset = self.style['wavegraph'].get_align("vertical-align", 0.5)
		y_size = self.style['wavegraph'].get_align("height", 0.9)
		
		# Work out our extents
		y_total = max([total for (key, total) in self.series_set.totals()])
		self.y_scale = VerticalWavegraphScale(0, y_total)
		
		# Calculate the points
		cols = []
		self.xs = []
		
		for x, stack in self.series_set.stacks():
			self.xs.append(self.scale.get_point(x))
			
			# Collect the points
			ys = []
			total = 0
			for ser, val in stack:
				y = self.y_scale.get_point(val) * y_size
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
		self.calc_plot_height()
		self.points = [[(x*self.width, y*self.plot_height) for x, y in zip(self.xs, ys)] for ys in self.rows]
		if self.label_curves:
			self.calc_text_positions()
	
	
	def interpolate(self, points, accuracy):
		
		"""
		Adds extra points into a list of points, interpolated linearly.
		
		@param points: The points to interpolate
		@type points: list (of 2-tuples)
		@param accuracy: How many extra points to create between each pair.
		@type accuracy: int
		@rtype: list
		"""
		
		newpoints = []
		fractions = [x/float(accuracy+1) for x in range(1, accuracy+1)]
		
		for i in range(len(points)-1):
			oldx, oldy = points[i]
			#oldx = self.xs[i]
			newx, newy = points[i+1]
			#newx = self.xs[i+1]
			
			newpoints.append((oldx, oldy))
			for fraction in fractions:
				newpoints.append((oldx+(fraction*(newx-oldx)), oldy+(fraction*(newy-oldy))))
		
		newpoints.append((newx, newy))
		return newpoints
	
	
	def rect_union(self, (rect1, rect2)):
		
		a1, b1, a2, b2 = rect1
		x1, y1, x2, y2 = rect2
		
		left = min(a1, x1)
		right = max(a2, x2)
		top = max(b1, y1)
		if (b1 > y2) or (y1 > b2):
			bottom = top
		else:
			bottom = min(b2, y2)
		
		return (left, top, right, bottom)
	
	
	def get_text_ratio(self, text):
		from graphication.text import text_bounds
		
		w, h = text_bounds(text, 10, self.style['wavegraph curve label'].get_font())
		
		if h and w:
			return (w/float(h))
		else:
			return 1
	
	
	def get_text_size(self, ratio, (x1, y1, x2, y2)):
		
		width = abs(x2-x1)
		height = abs(y2-y1)
		
		if (width == 0) or (height == 0):
			return 0
		
		this_ratio = width/float(height)
		
		if this_ratio > ratio:
			return height
		else:
			return width/float(ratio)
	
	
	def calc_text_positions(self, accuracy=5, max_per_curve=20, spacing=200):
		
		"""
		Calculates the positions of the text.
		"""
		
		self.labels = []
		
		# For each series...
		for i in range(len(self.series_set)):
			# Get the series, and the label's width/height ratio
			series = self.series_set.get_series(i)
			ratio = self.get_text_ratio(series.title)
			
			# Get the curve points, and interpolate along them
			tops = self.interpolate(self.points[i], accuracy)
			bottoms = self.interpolate(self.points[i+1], accuracy)
			
			# Work out bounding boxes for these points
			boxes = []
			for i in range(len(tops)-1):
				tl = tops[i]
				tr = tops[i+1]
				bl = bottoms[i]
				br = bottoms[i+1]
				
				boxes.append((tl[0], max(tl[1], tr[1]), br[0], min(bl[1], br[1])))
			
			# Go through and union them to collect a set of bigger boxes
			bigboxes = [boxes]
			for i in range(accuracy*2):
				bigboxes.append(map(self.rect_union, off_zip(bigboxes[-1])))
			
			# Reduce that into a single list, rather than a list of lists
			bigboxes = reduce(lambda a, b: a+b, bigboxes)
			
			# Associate each box with its appropriate text size, then sort
			bigboxes = [(self.get_text_size(ratio, rect), rect) for rect in bigboxes]
			bigboxes.sort()
			bigboxes.reverse()
			
			# Choose boxes in order of decending size, so they don't overlap
			taken = []
			for box in bigboxes:
				
				# If we have enough boxes, break
				if len(taken) >= max_per_curve:
					break
				
				# Check this isn't too close
				text_size, (left, top, right, bottom) = box
				try:
					for taken_left, taken_right in taken:
						if abs(left - taken_left) < spacing:
							raise TooClose
						elif abs(right - taken_right) < spacing:
							raise TooClose
						elif abs(right - taken_left) < spacing:
							raise TooClose
						elif abs(left - taken_right) < spacing:
							raise TooClose
				except TooClose:
					continue
				
				# OK, use this one
				taken.append((left, right))
				self.labels.append((box, series.title))
	
	
	def calc_plot_height(self):
		
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
			
			max_height = max(max_height, height + padding)
		self.plot_height = self.height - max_height
	
	
	def render_debug(self, context):
		
		"""Renders the calculation rectangles"""
		
		context.save()
		context.set_source_rgba(*hex_to_rgba("#f006"))
		
		for (size, (x1, y1, x2, y2)), title in self.labels:
			context.rectangle(x1, y1, (x2-x1), (y2-y1))
			context.stroke()
		
		context.restore()
	
	
	def render(self, context, debug=False):
		
		context.save()
		
		# Draw the vertical scale, if necessary
		if self.vertical_scale:
			major_style = self.style['wavegraph grid#y.major']
			minor_style = self.style['wavegraph grid#y.minor']
			
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
		
		major_style = self.style['wavegraph grid#x.major']
		minor_style = self.style['wavegraph grid#x.minor']
		
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
			#context.text_path(title)
			
			context.set_line_width(line_style.get_float("width", 1))
			context.set_source_rgba(*line_style.get_color("color", "#aaa"))
			context.move_to(x, 0)
			context.line_to(x, self.plot_height + line_style.get_float("padding", 0))
			context.stroke()
			
		
		# Draw the strips
		smooth = self.style['wavegraph curve'].get_float("smoothness")
		
		i = -1
		for series in self.series_set:
			i += 1
			
			# Get the two lists of points
			tops = self.points[i]
			bottoms = self.points[i+1]
			
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
		
		# Draw the on-curve labels
		
		if self.label_curves:
			label_style = self.style['wavegraph curve label']
			
			dimming_top = label_style.get_float('dimming-top', 1)
			dimming_bottom = label_style.get_float('dimming-bottom', 0)
			
			r,g,b,a = label_style.get_color('color', '#fff')
			context.select_font_face(
				label_style.get_font(),
				label_style.get_cairo_font_style(),
				label_style.get_cairo_font_weight(),
			)
			
			# Draw the labels
			for (size, (x1, y1, x2, y2)), title in self.labels:
				# Set the colour, including dimming
				if size >= dimming_top:
					dim = 1
				elif size < dimming_bottom:
					dim = 0
				else:
					dim = (size-dimming_bottom) / float(dimming_top-dimming_bottom)
				context.set_source_rgba(r,g,b,a*dim)
				
				# Position outselves
				context.set_font_size(size * 0.9)
				x_bearing, y_bearing, width, height = context.text_extents(title)[:4]
				context.move_to(((x2+x1)/2.0) - width / 2 - x_bearing, ((y2+y1)/2.0) - height / 2 - y_bearing)
				
				# Draw the text. We use text_path because it looks prettier 
				# (on image surfaces, show_text coerces font paths to fit inside pixels)
				context.show_text(title)
				#context.text_path(title)
				
				context.fill()
			
			# If uncommented, will show the used text boxes
			#self.render_debug(context)
		
		context.restore()


class TooClose(Exception): pass

def off_zip(l, n=2):
	"""
	Offset zip; zips the list so it has tuples 
	whose elements have adjacent indexes.
	
	@param l: The list to operate on
	@type l: list
	@param n: The size of the tuples
	@type n: int
	"""
	
	ls = []
	for i in range(n-1):
		ls.append(l[i:-(n-i-1)])
	ls.append(l[n-1:])
	return zip(*ls)
