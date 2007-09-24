

class BaseScale(object):
	
	def __init__(self, min, max, step=None, padding=None):
		
		"""
		Constructor.
		
		@param min: The minimum value to display on the scale.
		@param max: The maximum value to display on the scale.
		@param step: The value at multiples of which to draw gridlines.
		"""
		
		if step is None:
			step = self.__class__.default_step
		assert step > 0, "You must have a positive, non-zero step."
		
		if padding is None:
			padding = self.__class__.default_padding
		
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


class SimpleScale(BaseScale):
	
	default_step = 1
	default_padding = 0