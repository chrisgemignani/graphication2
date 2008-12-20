
from graphication.output import FileOutput
from graphication.color import hex_to_rgba

def write(self, filename):
	"""
	Saves the graph to a PNG file.
	
	@param filename: The name of the file to save to
	@type filename: str
	"""
	
	# Create an image context
	import cairo
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
	
	# Make sure it renders fonts using gray-based antialiasing
	font_options = surface.get_font_options()
	font_options.set_antialias(cairo.ANTIALIAS_GRAY)
	
	context = cairo.Context(surface)
	
	# Render the background
	context.set_source_rgba(*self.style['canvas.png'].get_color("background-color"))
	context.paint()
	
	context.set_antialias(cairo.ANTIALIAS_GRAY)
	
	# Do the rendering
	self.render_loop(context)
	
	# Write to a png
	surface.write_to_png(filename)
	surface.finish()


FileOutput.types['png'] = write