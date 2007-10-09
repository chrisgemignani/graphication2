
from graphication.output import FileOutput


def write(self, filename):
	"""
	Saves the graph to a PDF file.
	
	@param filename: The name of the file to save to
	@type filename: str
	"""
	
	# Create the SVG context
	import cairo
	surface = cairo.PDFSurface(filename, self.width, self.height)
	context = cairo.Context(surface)
	
	# Do the rendering
	self.render_loop(context)
	
	# Save the context
	context.show_page()
	surface.finish()


FileOutput.types['pdf'] = write