
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
		self.calc_positions()
	
	
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
				newpoints.append((oldx+(fraction*newx), oldy+(fraction*newy)))
		
		newpoints.append(newx, newy)
		return newpoints
	
	
	def calc_positions(self, accuracy=5):
		
		"""
		Calculates the positions of the text.
		"""
		
		for i in range(len(self.wavegraph.mseries.series)):
			series = self.wavegraph.mseries.get_series[i]
			
			tops = self.interpolate(self.wavegraph.points[i], accuracy)
			bottoms = self.interpolate(self.wavegraph.points[i+1], accuracy)
			
			boxes = [(l,t,r,b) for (l,t), (r,b) in zip(tops[:-1], bottoms[1:])]
			print boxes
		
	
	def render(self, context):
		
		"""
		Renders the text onto the specified context.
		Its size will match the WaveGraphCurves it was passed, you should ensure it's lined up.
		
		@param context: The context to render onto.
		@type content: cairo.Context
		"""
		
		pass



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