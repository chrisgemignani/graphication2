
from graphication.color import hex_to_rgba

class SubSeries(object):
	
	"""Holds one subset of data, with values and a title."""
	
	def __init__(self, title, values, color="#000000ff"):
		self.title = title
		self.values = values
		self.color = color.replace("#", "")
	
	
	def color_as_rgba(self):
		return hex_to_rgba(self.color)
	
	
	def __iter__(self):
		return iter(self.values)
	
	
	def __getitem__(self, key):
		return self.values[key]
	
	
	def __len__(self):
		return len(self.values)



class MultiSeries(object):
	
	"""A MultiSeries holds one or more sets of data points, 
	which all share common key values."""
	
	def __init__(self, keys):
		
		"""Constructor. Creates a MultiSeries, which you can add series to using add_series.
		
		@param keys: The key values for these series
		@type keys: list
		"""
		
		assert self.distinct(keys), "You must pass a list of keys which has distinct values."
		
		try:
			self.keys = map(float, keys)
		except ValueError:
			raise ValueError("All keys must be numeric")
		
		self.keys.sort()
		self.series = []
	
	
	def distinct(self, list):
		for i in range(len(list)):
			if list.index(list[i]) != i:
				return False
		return True
	
	
	def add_series(self, series):
		assert len(series) == len(self.keys), "You must pass the right size SubSeries for the number of keys."
		self.series.append(series)
	
	
	def items(self):
		
		"""Generator, which yields tuples of (key, [value, ...])"""
		
		for i in range(len(self.keys)):
			key = self.keys[i]
			values = []
			for serie in self.series:
				values.append(serie[i])
			yield (key, values)
	
	
	def get(self, key):
		
		"""Returns a list of values for the given key."""
		
		i = self.keys.index(key)
		
		return [serie[i] for serie in self.series]
	
	
	def get_series(self, index):
		
		"""Returns the series at the given index."""
		
		return self.series[index]
	
	
	def totals(self):
		
		"""Returns a list of sums of each key's values"""
		
		totals = []
		for (key, values) in self.items():
			totals.append(sum(values))
		return totals
	
	
	def titles(self):
		
		"""Returns an iterable of series titles, in order."""
		
		for serie in self.series:
			yield serie.title