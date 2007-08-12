
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
		
		# Get the font weight, and the font
		weights = {
			"normal": cairo.FONT_WEIGHT_NORMAL,
			"bold": cairo.FONT_WEIGHT_BOLD,
		}
		weight = weights[self.style["label:font_weight"].lower()]
		font = self.style["label:font"]
		
		# Work out the alignment (should be a keyword or a float)
		try:
			align = {
				"left": 0,
				"center": 0.5,
				"centre": 0.5,
				"right": 1,
			}.get(self.style["label:align"].lower(), self.style["label:align"])
			align = float(align)
		except ValueError:
			raise ValueError("'%s' is not a valid alignment value." % self.style["label:align"])
		
		# Fit the text to our box
		text_size = get_text_size(self.text, self.width, self.height, font, weight)
		
		# Prepare the context
		context.save()
		context.set_source_rgba(*hex_to_rgba(self.style["label:label_color"]))
		context.select_font_face(font, cairo.FONT_SLANT_NORMAL, weight)
		context.set_font_size(text_size * self.style["label:vertical_extent"])
		
		# Draw the text
		x_bearing, y_bearing, width, height = context.text_extents(self.text)[:4]
		context.move_to(
			(align*2)*self.width/2.0 - (align*2)*width / 2.0 - x_bearing,
			self.height/2.0 - height / 2.0 - y_bearing
		)
		
		context.show_text(self.text)
		context.restore()