
from graphication import default_css, Series
from graphication.text import text_bounds
from graphication.color import hex_to_rgba

class VerticalLines(object):
	
	def __init__(self, style, vertical_scale, vertical_label=None):
		
		"""
		Constructor; creates a new VerticalLines - a scale on the left
		and lines behind the graph
		
		@param vertical_scale: The vertical scale to use
		@type vertical_scale: graphication.scale.BaseScale
		
		@param vertical_label: The label to put next to the scale, if any.
		@type vertical_label: str
		"""
		
		self.style = style
		self.vertical_scale = vertical_scale
		self.vertical_label = vertical_label
	
	
	def set_size(self, width, height):
		self.width = width
		self.height = height
	
	
	def render(self, context, debug=False):
		
		context.save()
		
		fascent, fdescent, fheight, fxadvance, fyadvance = context.font_extents()
		
		major_style = self.style['verticallines grid#y.major']
		minor_style = self.style['verticallines grid#y.minor']
		
		for linepos, title, ismajor in self.vertical_scale.get_lines():
		
			if ismajor:
				this_style = major_style
			else:
				this_style = minor_style
			
			line_style = this_style.sub('line')
			label_style = this_style.sub('label')
			
			context.select_font_face(
				label_style.get_font(),
				label_style.get_cairo_font_style(),
				label_style.get_cairo_font_weight(),
			)
			context.set_font_size( label_style.get_float("font-size") )
			context.set_font_options(label_style.get_cairo_font_options())
			
			y = linepos * self.height
			
			x_bearing, y_bearing, width, height = context.text_extents(title)[:4]
			
			padding = label_style.get_float("padding")
			align = label_style.get_align("text-align")
			
			context.move_to(0 - padding - (align * width), y + fheight / 2.0 - fdescent)
			context.set_source_rgba(*label_style.get_color("color"))
			context.show_text(title)
			
			context.set_line_width(line_style.get_float("width", 1))
			context.set_source_rgba(*line_style.get_color("color", "#aaa"))
			
			context.move_to(0 - line_style.get_float("padding", 0), y)
			context.line_to(self.width, y)
			context.stroke()
		
		# Add the vertical scale's label if there is one
		if self.vertical_label:
			vlabel_style = self.style['verticallines vlabel']
			padding = vlabel_style.get_float("padding")
			align = vlabel_style.get_align("text-align")
			context.set_font_options(vlabel_style.get_cairo_font_options())
			x_bearing, y_bearing,  width, height = context.text_extents(self.vertical_label)[:4]
			context.move_to(0 - padding - (align * width), 18 + self.height - fdescent)
			context.set_source_rgba(*vlabel_style.get_color("color"))
			context.show_text(self.vertical_label)
		
		context.restore()

