

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
		if not getattr(self.__class__, 'allow_zero_step', False):
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
		real_max = self.max - self.padding
		x = real_min - (real_min % self.step)
		while x <= real_max:
			yield self.get_point(x), str(x), True
			x += self.step
	
	
	def get_point(self, value):
		
		try:
			return (value - self.min) / self.range
		except ZeroDivisionError:
			return 0
	
	
	def get_value(self, point):
		
		return (point * self.range) + self.min
	
	
	def label_for(self, point):
		
		return ""
	
	
	def is_secondary(self, date):
		
		return False


class SimpleScale(BaseScale):
	
	default_step = 1
	default_padding = 0


class VerticalWavegraphScale(BaseScale):
	
	default_step = None
	default_padding = 0
	allow_zero_step = True
	
	def get_lines(self):
		"""Yields (linepos, title, ismajor) tuples."""
		import math
		
		# Stop silly singularity errors occurring
		if self.range == 0: return
		
		if not self.step:
			self.step = (10 ** (math.ceil(math.log10(self.range)) - 1))
			if self.range / self.step < 4:
				self.step /= 2
		
		if self.step < 1:
			dp = math.ceil(abs(math.log10(self.step)))
		else:
			dp = 0
		
		real_min = self.min + self.padding
		real_max = self.max - self.padding
		x = real_max - (real_max % self.step)
		while x >= real_min :
			yield self.get_point(real_max - x), ("%%.%if" % dp) % x, True
			x -= self.step