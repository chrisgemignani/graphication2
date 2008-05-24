
import cairo

def get_text_size(text, box_width, box_height, font="Sans", weight=cairo.FONT_WEIGHT_NORMAL):
	
	"""
	Returns the text size needed to fit the given text inside the given size box.
	
	@param text: The text to size.
	@type text: str
	
	@param box_width: The width of the box to fit into
	@type box_width: float
	
	@param box_height: The height of the box to fit into
	@type box_height: float
	
	@param font: The font face to size
	@type font: str
	
	@param weight: The font weight
	@type weight: cairo.FONT_WEIGHT_NORMAL or cairo.FONT_WEIGHT_BOLD
	"""
	
	width, height = text_bounds(text, 10, font, weight)
	
	if not width or not height:
		return 0
	
	ratio = width/float(height)
	
	if (box_width == 0) or (box_height == 0):
		return 0
	
	box_ratio = box_width/float(box_height)
	
	if box_ratio > ratio:
		return box_height
	else:
		return box_width/float(ratio)


def text_bounds(text, size, font="Sans", weight=cairo.FONT_WEIGHT_NORMAL, style=cairo.FONT_SLANT_NORMAL):
	
	if not text:
		return 0, 0 # else cairo crashes
	
	# Create a new surface and context
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
	context = cairo.Context(surface)
	
	context.select_font_face(font, style, weight)
	context.set_font_size(size)
	
	width, height = context.text_extents(text)[2:4]
	return width, height
