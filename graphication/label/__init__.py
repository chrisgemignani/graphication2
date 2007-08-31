
import cairo
from graphication.text import get_text_size
from graphication.color import hex_to_rgba

class Label(object):
	
	def __init__(self, text, style):
		
		"""
		Constructor.
		
		@param text: The text of the label
		@type text: str
		@param style: The style to apply
		@type style: graphication.style.Style
		"""
		
		self.text = text
		self.style = style
	
	
	def set_size(self, width, height):
		self.width = width
		self.height = height
	
	
	def render(self, context):
		
		props = self.style['label']
		
		# Get the font weight, and the font
		weights = {
			"normal": cairo.FONT_WEIGHT_NORMAL,
			"bold": cairo.FONT_WEIGHT_BOLD,
		}
		weight = weights[props.get_weight("font-weight")]
		font = props.get("font-family", None)
		
		# Get the alignment
		align = props.get_align("text-align")
		color = props.get_color("color")
		height = props.get_align("height", 1.0)
		
		# Fit the text to our box
		text_size = get_text_size(self.text, self.width, self.height, font, weight)
		
		# Prepare the context
		context.save()
		context.set_source_rgba(*color)
		context.select_font_face(font, cairo.FONT_SLANT_NORMAL, weight)
		context.set_font_size(text_size * height)
		
		# Draw the text
		x_bearing, y_bearing, width, height = context.text_extents(self.text)[:4]
		context.move_to(
			(align*2)*self.width/2.0 - (align*2)*width / 2.0 - x_bearing,
			self.height/2.0 - height / 2.0 - y_bearing
		)
		
		context.show_text(self.text)
		context.restore()