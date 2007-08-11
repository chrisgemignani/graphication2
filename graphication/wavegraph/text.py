
import cairo
from graphication.color import hex_to_rgba

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


class WaveGraphCurveLabels(object):
	
	def __init__(self, wavegraph):
		
		"""
		Constructor.
		
		@param wavegraph: The WaveGraphCurves to plot from.
		@type wavegraph: WaveGraphCurves
		"""
		
		self.wavegraph = wavegraph
	
	
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
			newx, newy = points[i+1]
			
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
		return len(text)/1.8
	
	
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
	
	
	def calc_positions(self, accuracy=5):
		
		"""
		Calculates the positions of the text.
		"""
		
		self.labels = []
		
		# For each series...
		for i in range(len(self.wavegraph.mseries.series)):
			# Get the series, and the label's width/height ratio
			series = self.wavegraph.mseries.get_series(i)
			ratio = self.get_text_ratio(series.title)
			
			# Get the curve points, and interpolate along them
			tops = self.interpolate(self.wavegraph.points[i], accuracy)
			bottoms = self.interpolate(self.wavegraph.points[i+1], accuracy)
			
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
			
			self.labels.append((bigboxes[-1], series.title))
	
	
	def render_debug(self, context):
		
		"""Renders the calculation rectangles"""
		
		context.save()
		context.set_source_rgba(*hex_to_rgba("#f006"))
		
		for (size, (x1, y1, x2, y2)), title in self.labels:
			context.rectangle(x1, y1, x2-x1, y2-y1)
			context.stroke()
		
		context.restore()
		
	
	def render(self, context, color, font="Sans", weight="normal", vertical_extent=0.8, dimming_top=0, dimming_bottom=0):
		
		"""
		Renders the text onto the specified context.
		Its size will match the WaveGraphCurves it was passed, you should ensure it's lined up.
		
		@param context: The context to render onto.
		@type content: cairo.Context
		"""
		
		weights = {
			"normal": cairo.FONT_WEIGHT_NORMAL,
			"bold": cairo.FONT_WEIGHT_BOLD,
		}
		
		# Initialise context
		context.save()
		r,g,b,a = hex_to_rgba(color)
		context.select_font_face(font, cairo.FONT_SLANT_NORMAL, weights[weight.lower()])
		
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
			context.set_font_size(size*vertical_extent)
			x_bearing, y_bearing, width, height = context.text_extents(title)[:4]
			context.move_to(((x2+x1)/2.0) - width / 2 - x_bearing, ((y2+y1)/2.0) - height / 2 - y_bearing)
			
			# Draw the text. We use text_path because it looks prettier 
			# (on image surfaces, show_text coerces font paths to fit inside pixels)
			#context.show_text(title)
			context.text_path(title)
			
			context.fill()
		
		context.restore()



class WaveGraphAxisLabels(object):
	
	"""
	Renders textual labels along the horizontal axis.
	"""
	
	def __init__(self, wavegraph, labels):
		
		"""
		Constructor.
		
		@param wavegraph: The WaveGraphCurves to plot from.
		@type wavegraph: WaveGraphCurves
		@param labels: A dict, where the keys are the x-values and the values the text to label with.
		@type labels: dict
		"""
		
		self.wavegraph = wavegraph
		self.labels = labels
	
	
	def set_size(self, width, height):
		
		self.width = width
		self.height = height
		self.line1_height = self.height / 3.0
		self.line2_height = 2*self.height / 3.0
		self.mid_height = self.height / 2.0
		
		self.xs = [ ((x - self.wavegraph.min_x) * self.wavegraph.scale_x * self.width, label) for x, label in self.labels.items() ]
	
	
	def render(self, context, color, size=15, font="Sans"):
		
		context.save()
		context.set_source_rgba(*hex_to_rgba(color))
		context.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		context.set_font_size(size)
		
		for x, text in self.xs:
			if "\n" in text:
				line1, line2 = text.split("\n", 1)
				x_bearing, y_bearing, width, height = context.text_extents(line1)[:4]
				context.move_to(x - width / 2 - x_bearing, self.line1_height - height / 2 - y_bearing)
				context.show_text(line1)
				x_bearing, y_bearing, width, height = context.text_extents(line2)[:4]
				context.move_to(x - width / 2 - x_bearing, self.line2_height - height / 2 - y_bearing)
				context.show_text(line2)
			else:
				x_bearing, y_bearing, width, height = context.text_extents(text)[:4]
				context.move_to(x - width / 2 - x_bearing, self.mid_height - height / 2 - y_bearing)
				context.show_text(text)
		
		context.restore()