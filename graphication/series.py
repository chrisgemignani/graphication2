
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



class Series(object):
	
	"""
	A single dataset. Has a series of points, a title and a color.
	
	Iterate over it to recieve (key, value) pairs, in-order.
	"""
	
	def __init__(self, points, title="Series", color="#036"):
		"""
		Constructor.
		
		@param points: A dict of points to plot. Keys are the 'primary' values, values are their respective... values.
		@type points: dict
		
		@param title: The title of the series
		@type title: string
		
		@param color: The colour to draw the series
		@type color: string
		"""
		
		self.points = points
		self.title = title
		self.color = color
	
	
	def __iter__(self):
		items = self.points.items()
		items.sort()
		for item in items:
			yield item
	
	
	def key_range(self):
		"""Returns a tuple of (min, max, range) for the set of key values."""
		keys = self.points.keys()
		this_max = max(keys)
		this_min = min(keys)
		return (this_min, this_max, this_max-this_min)
	
	
	def value_range(self):
		"""Returns a tuple of (min, max, range) for the set of value values."""
		values = self.points.values()
		this_max = max(values)
		this_min = min(values)
		return (this_min, this_max, this_max-this_min)


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