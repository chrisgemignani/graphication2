
from graphication.scales import BaseScale
import time
import datetime


def d_to_timestamp(d):
	if isinstance(d, (int, float)):
		return d
	return time.mktime(d.timetuple())

def timestamp_to_d(t):
	if isinstance(t, (datetime.datetime, datetime.date)):
		return t
	return datetime.datetime.fromtimestamp(t)

class DateScale(BaseScale):
	
	def __init__(self, min, max, step=None, padding=None, minor_step=None):
		
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
		
		if minor_step is None:
			minor_step = 86400
		assert minor_step > 0, "You must have a positive, non-zero minor step."
		
		if padding is None:
			padding = 0
		
		min = d_to_timestamp(min)
		max = d_to_timestamp(max)
		
		self.min = min - padding
		self.max = max + padding
		self.padding = padding
		self.range = float(self.max - self.min)
		self.step = step
		self.minor_step = minor_step
	
	
	def get_lines(self):
		
		"""Yields (linepos, title, ismajor) tuples."""
		
		x = real_min = self.min + self.padding
		while x <= self.max - self.padding:
			yield self.get_point(x), "", False
			x += self.minor_step
		
		x = real_min = self.min + self.padding
		while x <= self.max - self.padding:
			yield self.get_point(x), self.niceify_date(x), True
			x += self.step
	
	
	def get_point(self, value):
		value = d_to_timestamp(value)
		try:
			return (value - self.min) / self.range
		except ZeroDivisionError:
			return 0
	
	
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
	
	def __init__(self, series_set, step=None, minor_step=None):
		self.min, self.max = map(d_to_timestamp, series_set.key_range())
		self.range = float(self.max - self.min)
		self.padding = 0
		
		if step is None:
			step = 86400 * 7
		
		if minor_step is None:
			minor_step = 86400
		
		assert step > 0, "You must have a positive, non-zero step."
		assert minor_step > 0, "You must have a positive, non-zero minor step."
		self.step = step
		self.minor_step = minor_step


def week_beginning(date):
	return date - datetime.timedelta(0 - date.weekday())


def week_range(start, end):
	now = week_beginning(start) + datetime.timedelta(1)
	while now < end:
		if now > start:
			yield now
		now += datetime.timedelta(7)


def month_beginning(date):
	return date.replace(day=1)


def month_range(start, end):
	now = month_beginning(start)
	while now < end:
		if now > start:
			yield now
		now += datetime.timedelta(32)
		now = month_beginning(now)



class AutoWeekDateScale(DateScale):
	
	"""
	A special DateScale that takes in a SeriesSet and a step to
	display with, rather than minima and maxima, and highlights
	weeks with minor lines and months with major lines.
	"""
	
	def __init__(self, series_set, short_labels=False, month_gap=1):
		self.min, self.max = map(d_to_timestamp, series_set.key_range())
		self.range = float(self.max - self.min)
		self.short_labels = short_labels
		self.month_gap = month_gap
	
	
	def get_lines(self):
		
		"""Yields (linepos, title, ismajor) tuples."""
		
		start = datetime.datetime.fromtimestamp(self.min)
		end = datetime.datetime.fromtimestamp(self.max)
		
		current_year = None
		
		if self.short_labels:
			m_fmt, my_fmt = "%b", "%b %y"
		else:
			m_fmt, my_fmt = "%B", "%B %Y"
		
		for week in week_range(start, end):
			yield (self.get_point(week), "", False)
		
		for i, month in enumerate(month_range(start, end)):
			if i % self.month_gap == 0:
				new_current_year = month.strftime("%Y")
				if new_current_year != current_year:
					yield (self.get_point(month), month.strftime(my_fmt), True)
				else:
					yield (self.get_point(month), month.strftime(m_fmt), True)
				current_year = new_current_year



class WeekdayDateScale(DateScale):
	
	"""
	A DateScale which only plots points on weekdays, reducing weekends
	to infinitely small lines.
	"""
	
	def __init__(self, *a, **kw):
		DateScale.__init__(self, *a, **kw)
		# Adjust range to rescale
		self.range *= (5/7.0)
	
	def get_point(self, value):
		# Get values in each type
		value = d_to_timestamp(value)
		# Work out the step-per-day
		try:
			step = 86400 / self.range
		except ZeroDivisionError:
			return 0
		# Starting at the min, step through the days adding only the weekdays
		vpos = self.min
		pos = 0
		while vpos < value:
			if timestamp_to_d(vpos).weekday() < 5:
				pos += step
			vpos += 86400
		return pos