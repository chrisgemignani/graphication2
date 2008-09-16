"""
Output modules
"""

import os
from graphication import default_css

class FileOutput(object):
	
	"""
	Base class for output. Has methods for item management and layout calculations.
	"""
	
	types = {}
	
	def __init__(self, style=None, padding=0):
		self.style = default_css.merge(style)
		self.items = []
		self.padding = padding
	
	
	def add_item(self, item, x, y, width, height):
		"""Adds an item to this Output. Pass in its position and size, as floats or ints."""
		
		entry = (item, (x,y), (width, height))
		
		if entry not in self.items:
			self.items.append(entry)
	
	
	def calculate_size(self):
		"""Calculates the bounds of the page"""
		right, bottom = 0,0
		for item, (x, y), (w, h) in self.items:
			if x + w > right:
				right = x + w
			if y + h > bottom:
				bottom = y + h
		return (right+self.padding*2, bottom+self.padding*2)
	
	
	def render_loop(self, context):
		"""Renders items in a generic fashion. Should be passed a context."""
		for item, (x, y), (w, h) in self.items:
			context.save()
			context.translate(x+self.padding, y+self.padding)
			item.set_size(w, h)
			item.render(context)
			context.restore()
	
	def write(self, type, destination):
		if not hasattr(self, "width"):
			self.width, self.height = self.calculate_size()
		if type not in self.types:
			raise ValueError("Don't know how to write type '%s'." % type)
		return self.types[type](self, destination)
	
	
	def stream(self, type):
		import tempfile
		filename = tempfile.mkstemp()[1]
		self.write(type, filename)
		fo = open(filename)
		os.unlink(filename)
		return fo


import graphication.output.svg
import graphication.output.svgz
import graphication.output.png
import graphication.output.pdf