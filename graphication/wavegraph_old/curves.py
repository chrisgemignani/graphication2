
from graphication.color import hex_to_rgba

class WaveGraphCurves(object):
	
	def __init__(self, mseries, yoffset=0.5, vextent=1.0):
		
		"""
		Constructor. Pass it a MultiSeries to plot, in top-to-bottom order.
		
		@param mseries: MultiSeries to plot
		@type mseries: MultiSeries
		"""
		
		self.yoffset = yoffset
		self.vextent = vextent
		self.mseries = mseries
		self.calc_rel_points()
		
		self.width = None
		self.height = None
	
	
	def calc_rel_points(self):
		
		"""Calculates the relative shapes of the sections"""
		
		self.totals = self.mseries.totals()
		
		max_y = max(self.totals)
		scale_y = self.vextent / max_y
		padding = ((1-self.vextent) / 2.0)
		
		self.yss = [map(lambda y: scale_y * (max_y*self.yoffset - y*self.yoffset) + padding, self.totals)]
		for i in range(len(self.mseries.series)):
			series = self.mseries.get_series(i)
			self.yss.append([o + (t*scale_y) for o,t in zip(self.yss[i], series.values)])
		
		keys = self.mseries.keys
		self.min_x = keys[0]
		self.delta_x = keys[-1] - self.min_x
		self.scale_x = 1.0 / self.delta_x
		self.xs = [ (x - self.min_x) * self.scale_x for x in keys ]
	
	
	def calc_real_points(self):
		
		self.points = []
		
		for ys in self.yss:
			self.points.append([(x*self.width, y*self.height) for x, y in zip(self.xs, ys)])
		
		return self.points
	
	
	def set_size(self, width, height):
		if (self.width != width) or (self.height != height):
			self.width = width
			self.height = height
			self.calc_real_points()
	
	
	def render(self, context, smooth=0.25):
		
		"""
		Render the wavegraph onto a cairo context.
		
		@param context: The Cairo context to render onto
		@type context: cairo.Context
		"""
		
		# Draw the strips
		for i in range(len(self.mseries.series)):
			
			series = self.mseries.get_series(i)
			tops = self.points[i]
			bottoms = self.points[i+1]
			
			context.move_to(*tops[0])
			for i in range(1, len(tops)):
				ox, oy = tops[i-1]
				nx, ny = tops[i]
				dx = (nx - ox) * smooth
				context.curve_to(ox+dx, oy, nx-dx, ny, nx, ny)
			
			context.line_to(*bottoms[-1])
			for i in range(2, len(bottoms)+1):
				ox, oy = bottoms[-(i-1)]
				nx, ny = bottoms[-i]
				dx = (nx - ox) * smooth
				context.curve_to(ox+dx, oy, nx-dx, ny, nx, ny)
			
			context.set_source_rgba(*series.color_as_rgba())
			context.close_path()
			context.fill()
