
from graphication.output import FileOutput
import os

def write(self, filename):
	"""
	Saves the graph to a SVGZ file.
	
	@param filename: The name of the file to save to
	@type filename: str
	"""
	
	# Create the svg filename
	import tempfile
	svg_filename = tempfile.mkstemp()[1]
	
	# Create the SVG context
	import cairo
	surface = cairo.SVGSurface(svg_filename, self.width, self.height)
	context = cairo.Context(surface)
	
	# Do the rendering
	self.render_loop(context)
	
	# Save the context
	context.show_page()
	surface.finish()
	
	# Compress the file
	os.system("gzip -c %s > %s" % (svg_filename, filename))
	os.unlink(svg_filename)


FileOutput.types['svgz'] = write