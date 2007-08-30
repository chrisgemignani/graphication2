

class BaseScale(object):
	pass


class SimpleScale(BaseScale):
	
	def __init__(self, min, max, step, padding=0):
		
		"""
		Constructor.
		
		@param min: The minimum value to display on the scale.
		@param max: The maximum value to display on the scale.
		@param step: The value at multiples of which to draw gridlines.
		"""
		
		self.min = min - padding
		self.max = max + padding
		self.padding = padding
		self.range = float(self.max - self.min)
		self.step = step
	
	
	def get_lines(self):
		
		"""Yields (linepos, title, ismajor) tuples."""
		
		real_min = self.min + self.padding
		x = real_min - (real_min % self.step)
		while x <= self.max - self.padding:
			yield self.get_point(x), str(x), True
			x += self.step
	
	
	def get_point(self, value):
		
		return (value - self.min) / self.range