
from graphication.output import FileOutput
from graphication.color import hex_to_rgba

def write(self, filename):
	"""
	Saves the graph to a SVG file.
	
	@param filename: The name of the file to save to
	@type filename: str
	"""
	
	# Create a SVG context
	import cairo
	width, height = self.calculate_size()
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
	context = cairo.Context(surface)
	
	# Render the background
	context.set_source_rgba(*hex_to_rgba(self.style['png:background']))
	context.paint()
	
	# Do the rendering
	self.render_loop(context)
	
	# Write to a png
	surface.write_to_png('test.png')
	surface.finish()


FileOutput.types['png'] = write