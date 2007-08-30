
from graphication.color import hex_to_rgba

class WaveGraphVGrid(object):
	
	"""
	A WaveGraphVGrid renders a (horizontal axis, vertical lines) grid suitable for positioning behind a WaveGraph.
	"""
	
	def __init__(self, wavegraph, xs):
		
		"""
		Constructor.
		
		@param wavegraph: The WaveGraphCurves to plot from.
		@type wavegraph: WaveGraphCurves
		@param xs: A list of x values to draw grid lines at
		@type xs: list
		"""
		
		self.wavegraph = wavegraph
		self.xs = xs
		
		self.width = None
		self.height = None
	
	
	def set_size(self, width, height):
		if (self.width != width) or (self.height != height):
			self.width = width
			self.height = height
			self.real_xs = [ (x - self.wavegraph.min_x) * self.wavegraph.scale_x * self.width for x in self.xs ]
	
	
	def render(self, context, color, thickness=2):
		
		context.save()
		context.set_line_width(thickness)
		context.set_source_rgba(*hex_to_rgba(color))
		
		for x in self.real_xs:
			context.move_to(x, 0)
			context.line_to(x, self.height)
			context.stroke()
		
		context.restore()



class WaveGraphScale(object):
	pass