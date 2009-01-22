
from graphication.css import hex_to_rgba


class OrderedDict(object):
	
	def __init__(self, pairs):
		self.dict = {}
		self.ordered = []
		for key, value in pairs:
			self.dict[key] = value
			self.ordered.append(key)
	
	def order(self):
		self.ordered = self.dict.keys()
		self.ordered.sort()
	
	def keys(self):
		return self.ordered
	
	def values(self):
		return [self.dict[x] for x in self.ordered]
	
	def items(self):
		return [(x, self.dict[x]) for x in self.ordered]
	
	def __getitem__(self, key):
		return self.dict[key]
	
	def __setitem__(self, key, value):
		self.dict[key] = value
		if key not in self.dict:
			self.ordered.append(key)



class Series(object):
	
	"""Holds one set of data, with keys, values and a title."""
	
	STYLE_NONE = 0
	STYLE_DASHED = 1
	STYLE_LIGHT = 2
	STYLE_VLIGHT = 3
	STYLE_LINETOP = 4
	STYLE_DOUBLEFILL = 5
	STYLE_WHOLEFILL = 6
	
	def __init__(self, title, data, color="#000000ff", styles={}, fill_color=None, line_width=None):
		self.title = title
		self.data = data
		self.color = color.replace("#", "")
		self.styles = styles
		self.fill_color = fill_color
		self.line_width = line_width
	
	
	def color_as_rgba(self):
		return hex_to_rgba(self.color)
	
	
	def fill_color_as_rgba(self):
		if self.fill_color:
			return hex_to_rgba(self.fill_color)
		else:
			return None
	
	
	def keys(self):
		return map(lambda (x,y): x, self.items())
	
	
	def values(self):
		return map(lambda (x,y): y, self.items())
	
	
	def sum(self):
		return sum(self.values())
	
	
	def items(self):
		items = self.data.items()
		items.sort()
		return items
	
	
	def key_range(self):
		keys = self.data.keys()
		if len(keys) == 0:
			return None, None
		return min(keys), max(keys)
	
	
	def value_range(self):
		values = self.data.values()
		if len(values) == 0:
			return None, None
		return min(values), max(values)
	
	
	def __iter__(self):
		return iter(self.data)
	
	
	def __getitem__(self, key):
		return self.data[key]
	
	
	def __len__(self):
		return len(self.data)
	
	
	def __str__(self):
		kr = self.key_range()
		return "%d values, keys between %s and %s" % (len(self), kr[0], kr[1]) 
	
	
	def __sub__(self, other):
		assert isinstance(other, Series)
		newdata = dict([
			(k, max(v - other[k], 0))
			for k, v in self.data.items()
		])
		return Series(self.title, newdata, self.color, self.styles, self.fill_color)
	
	
	def interpolate(self, key):
		"""
		Returns the value at 'key', with linear interpolation, and
		constant extrapolation.
		"""
		
		keys = self.keys()
		
		if not keys:
			raise ValueError("No values to interpolate between.")
		
		if key in keys:
			return self.data[key]
		
		pre = keys[0]
		post = None
		
		# Check to see if it needs to be extrapolated below.
		if key < pre:
			return self.data[pre]
		
		# Get the two values above and below it
		for a_key in keys:
			if a_key > key:
				post = a_key
				break
			else:
				pre = a_key
		
		# Extrapolate above?
		if post is None:
			return self.data[pre]
		
		# Interpolate
		range = post - pre
		pc = (key - pre)
		
		import datetime
		if isinstance(range, datetime.timedelta):
			pc = pc.days
			range = range.days
		pc = pc / float(range)
		
		bottom = self.data[pre]
		top = self.data[post]
		vrange = top - bottom
		return bottom + (vrange * pc)
	
	
	def __getslice__(self, start, end):
		newdata = {}
		for key, value in self.data:
			if key >= start and key <= end:
				newdata[key] = value
		return Series(self.title, newdata, self.color, self.styles)
	
	
	def split_at(self, positions):
		"""Splits this series into several series at the given
		positions."""
		
		start = 0
		seriess = []
		for position in positions:
			seriess.append(self[start:position])
			start = position
		seriess.append(self[start:])
	
	
	def style_at(self, key):
		"""Returns the style at the given key."""
		matches = [x for x in self.styles.keys() if x <= key]
		matches.sort()
		if matches:
			return self.styles[matches[-1]]
		else:
			return 0



class SeriesSet(object):
	
	"""
	SeriesSets hold zero or more Series.
	They have useful operations such as overall maxima, minima, etc.
	Iterating over one will yield the series one-by-one.
	"""
	
	def __init__(self, series=None):
		if series is None:
			self.series = []
		else:
			self.series = series
	
	
	def __iter__(self):
		return iter(self.series)
	
	
	def __len__(self):
		return len(self.series)
	
	
	def add_series(self, series):
		self.series.append(series)
	
	
	def key_range(self):
		assert len(self.series) > 0, "Cannot find the range of an empty set."
		mins, maxs = zip(*[series.key_range() for series in self.series])
		mins = [m for m in mins if m]
		maxs = [m for m in maxs if m]
		return min(mins), max(maxs)
	
	
	def value_range(self):
		assert len(self.series) > 0, "Cannot find the range of an empty set."
		mins, maxs = zip(*[series.value_range() for series in self.series])
		return min(mins), max(maxs)
	
	
	def sum(self):
		return sum([s.sum() for s in self.series])
	
	
	def keys(self, with_series=False):
		"""
		Returns all possible keys, in order.
		If 'with_series' is true, returns them as tuples, with the second element being the list
		of series they appear in.
		"""
		
		# TODO: This could be made a bit more efficient.
		
		keys = {}
		for series in self.series:
			for key in series.keys():
				keys[key] = keys.get(key, []) + [series]
		
		if with_series:
			keys = keys.items()
		else:
			keys = keys.keys()
		keys.sort()
		return keys
	
	
	def stack(self, key):
		"""Returns a list of (series, value-at-key) tuples for the series."""
		
		return map(lambda x:(x,x.interpolate(key)), self.series)
	
	
	def stacks(self):
		"""Returns a list of (key, stack) for each possible key."""
		
		return map(lambda x:(x, self.stack(x)), self.keys())
	
	
	def totals(self):
		"""Generates a list of (key, total-at-key) tuples, in key order."""
		
		for key in self.keys():
			yield key, sum(map(lambda x:x.interpolate(key), self.series))
	
	
	def get_series(self, index):
		"""Returns the index'th series."""
		return self.series[index]



class Node(object):
	
	"""
	Represents a node in a structure diagram.
	Has a single value, as well as attributes like title and color.
	"""
	
	def __init__(self, value, title="Node", color="#036"):
		
		self.value = value
		self.title = title
		self.color = color



class NodeLink(object):
	
	"""
	Represents a link between to Nodes.
	"""
	
	def __init__(self, start, end, weight=1, color="#600"):
		
		self.start = start
		self.end = end
		self.weight = weight
		self.color = color


class NodeSet(object):
	
	"""
	Contains many Nodes, as well as the relationships that link them together.
	"""
	
	def __init__(self):
		
		self.nodes = []
		self.links = []
	
	
	def add_node(self, node):
		"""Adds the given Node to the NodeSet."""
		self.nodes.append(node)
	
	
	def add_link(self, link):
		"""Links the first node to the second. Note that in some graphs, order might matter."""
		assert isinstance(link, NodeLink), "You must pass in a NodeLink"
		assert link.start in self.nodes, "The first node is not in this NodeSet."
		assert link.end in self.nodes, "The second node is not in this NodeSet."
		self.links.append(link)
	
	
	def adjacent_to(self, node, both=True):
		"""Returns a generator of all (othernode, link) tuples that are linked to this Node.
		
		@param node: The node to return nodes adjacent to.
		@param both: If we should use links in either direction (True) or only ones away (False)."""
		
		for link in self.links:
			if link.start == node:
				yield link.end, link
			elif link.end == node and both:
				yield link.start, link
	
	
	def value_range(self):
		"""Returns a tuple of (min, max, range) for the set of value values."""
		values = [node.value for node in self.nodes]
		this_max = max(values)
		this_min = min(values)
		return (this_min, this_max, this_max-this_min)
	
	
	def __iter__(self):
		return iter(self.nodes)
	
	
	def __getitem__(self, key):
		return self.nodes[key]
