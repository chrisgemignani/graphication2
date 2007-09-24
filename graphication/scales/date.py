
from graphication.scales import BaseScale
import time
import datetime


def d_to_timestamp(d):
	if isinstance(d, int) or isinstance(d, float):
		return d
	return time.mktime(d.timetuple())


class DateScale(BaseScale):
	
	def __init__(self, min, max, step=None, padding=None):
		
		"""
		Constructor.
		
		@param min: The minimum value to display on the scale.
		@param max: The maximum value to display on the scale.
		@param step: The value at multiples of which to draw gridlines. In seconds.
		@param padding: The amount of extra scale to have around the ends. In seconds.
		"""
		
		if step is None:
			step = 86400 * 7
		assert step > 0, "You must have a positive, non-zero step."
		
		if padding is None:
			padding = 0
		
		min = d_to_timestamp(min)
		max = d_to_timestamp(max)
		
		self.min = min - padding
		self.max = max + padding
		self.padding = padding
		self.range = float(self.max - self.min)
		self.step = step
	
	
	def get_lines(self):
		
		"""Yields (linepos, title, ismajor) tuples."""
		
		x = real_min = self.min + self.padding
		#x = real_min - (real_min % self.step)
		while x <= self.max - self.padding:
			print x
			yield self.get_point(x), self.niceify_date(x), True
			x += self.step
	
	
	def get_point(self, value):
		value = d_to_timestamp(value)
		return (value - self.min) / self.range
	
	
	def niceify_date(self, date):
		if self.step < 60:
			f = "%H:%M:%S"
		elif self.step < 3600:
			f = "%H:%M"
		elif self.step < 86400:
			f = "%I%p %d %b"
		elif self.step < 86400 * 7:
			f = "%d %b"
		elif self.step < 86400 * 29:
			f = "%d %b"
		elif self.step < 86400 * 365.25:
			f = "%b"
		return time.strftime(f, time.gmtime(date))


class AutoDateScale(DateScale):
	
	"""
	A special DateScale that takes in a SeriesSet and a step to
	display with, rather than minima and maxima.
	"""
	
	def __init__(self, series_set, step=None):
		self.min, self.max = map(d_to_timestamp, series_set.key_range())
		self.range = float(self.max - self.min)
		self.padding = 0
		
		if step is None:
			step = 86400 * 7
		
		assert step > 0, "You must have a positive, non-zero step."
		self.step = step