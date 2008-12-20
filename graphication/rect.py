
from graphication.color import hex_to_rgba

class Rect(object):
	
	"""
	A solid rectangle.
	"""
	
	def __init__(self, colour):
		self.colour = colour
	
	def set_size(self, width, height):
		self.width = width
		self.height = height
	
	def render(self, context, debug=False):
		context.set_source_rgba(*hex_to_rgba(self.colour))
		context.rectangle(0,0,self.width,self.height)
		context.fill()

