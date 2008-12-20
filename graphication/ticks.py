
from graphication import default_css, Series
from graphication.text import text_bounds
from graphication.color import hex_to_rgba
from graphication.scales import SimpleScale

class Ticks(object):
	
	"""
	Displays a horizontal scale as a line with labelled ticks.
	"""
	
	def __init__(self, scale, style=None, hide_first=False):
		
		"""
		Constructor; creates a new Ticks.
		
		@param scale: The Scale to use for the graph.
		@type scale: graphication.scales.BaseScale
		
		@param style: The Style to apply to this graph
		@type style: graphication.style.Style
		"""
		
		self.style = default_css.merge(style)
		self.scale = scale
		self.hide_first = hide_first
	
	
	def set_size(self, width, height):
		self.width = width
		self.height = height
	
	
	def render(self, context, debug=False):
		
		context.save()
		
		# Draw the horizontal line and ticks
		this_style = self.style['ticks']
		tick_style = this_style.sub('tick')
		label_style = this_style.sub('label')
		tick_length = tick_style.get_float('length', 5)
		context.set_source_rgba(*tick_style.get_color("color"))
		context.set_line_width(tick_style.get_float("width", 2))
		
		# Line across
		context.move_to(0, tick_length)
		context.line_to(self.width, tick_length)
		context.stroke()
		
		fascent, fdescent, fheight, fxadvance, fyadvance = context.font_extents()
		
		first = True
		
		for linepos, title, ismajor in self.scale.get_lines():
			
			if ismajor:
			
				if first and self.hide_first:
					first = False
					continue
				
				first = False
				
				# Draw tick
				context.set_source_rgba(*tick_style.get_color("color"))
				context.move_to(self.width * linepos, 0)
				context.line_to(self.width * linepos, tick_length)
				context.stroke()
				
				# Draw label
				context.set_source_rgba(*label_style.get_color("color"))
				context.select_font_face(
					label_style.get_font(),
					label_style.get_cairo_font_style(),
					label_style.get_cairo_font_weight(),
				)
				context.set_font_options(label_style.get_cairo_font_options())
				context.set_font_size( label_style.get_float("font-size") )
				
				x = linepos * self.width
				
				x_bearing, y_bearing, width, height = context.text_extents(title)[:4]
				align = label_style.get_align("align")
				padding = label_style.get_float("padding", 0)
				
				context.move_to(x - (align * width), (self.height-tick_length)/2.0 + padding + fheight / 2.0 - fdescent)
				context.show_text(title)
				context.fill()
		
		context.restore()

