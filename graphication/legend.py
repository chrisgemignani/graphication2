
import math
from graphication.color import hex_to_rgba
from graphication import css, default_css

class Legend(object):
	
	def __init__(self, series_set, style=None, dashed_name=None):
		
		"""
		Constructor; creates a new Legend.
		
		@param series_set: The data to label, as a SeriesSet
		@type series_set: graphication.series.SeriesSet
		
		@param style: The Style to apply to this legend.
		@type style: graphication.style.Style
		"""
		
		self.series_set = series_set
		self.dashed_name = dashed_name
		
		self.style = default_css.merge(style)
	
	
	def set_size(self, width, height):
		self.width = width
		self.height = height
		
		self.center_x = width / 2.0
		self.center_y = height / 2.0
	
	
	def render(self, context, debug=False):
		
		context.save()
		
		legend_style = self.style['legend']
		key_style = legend_style.sub('key')
		label_style = legend_style.sub('label')
		
		key_left = key_style.get_float("padding-left", 3)
		key_width = key_style.get_float("width", 15)
		key_height = key_style.get_float("height", 15)
		key_border_width = key_style.get_float("border-width", 1)
		key_border_color = key_style.get_color("border-color", "#555")
		label_left = key_left + key_width + key_style.get_float("padding-right", 3)
		
		# Work out how much vertical space we have for each series
		if legend_style.is_auto("line-height"):
			y_per_series = float(self.height) / (len(self.series_set) + int(bool(self.dashed_name))*2)
		else:
			y_per_series = legend_style.get_float("line-height", 15)
		
		y = y_per_series / 2.0
		
		for series in self.series_set:
			# Draw the key rectangle
			if series.style_at(0) == series.STYLE_LINETOP:
				context.rectangle(key_left, y - key_height/2.0, key_width, key_height)
				r,g,b,a = series.color_as_rgba()
				context.set_source_rgba(r,g,b,a*0.3)
				context.fill()
				context.set_source_rgba(r,g,b,a)
				context.set_line_width(3)
				context.move_to(key_left, y - key_height/2.0)
				context.line_to(key_left + key_width, y - key_height/2.0)
				context.stroke()
			else:
				context.rectangle(key_left, y - key_height/2.0, key_width, key_height)
				context.set_source_rgba(*series.color_as_rgba())
				context.fill_preserve()
				context.set_line_width(key_border_width)
				context.set_source_rgba(*key_border_color)
				context.stroke()
			
			# Draw the label
			context.select_font_face(
				label_style.get_font(),
				label_style.get_cairo_font_style(),
				label_style.get_cairo_font_weight(),
			)
			context.set_font_size( label_style.get_float("font-size") )
			
			x_bearing, y_bearing, width, height = context.text_extents(series.title)[:4]
			
			context.move_to(label_left - x_bearing, y + key_height/3.6)
			context.set_source_rgba(*label_style.get_color("color"))
			context.show_text(series.title)
			
			# Move down to the next series
			y += y_per_series
		
		if self.dashed_name:
			y += key_style.get_float("height", 3)
			# Draw the key rectangle
			left, top = key_left, y - key_height/2.0
			context.rectangle(left, top, key_width, key_height)
			import cairo
			linear = cairo.LinearGradient(left, top, left+key_width, top+key_height)
			r,g,b,a = 0,0,0,1
			for i in range(0, int(key_width), 3):
				dt = 1.0 / float(key_width)
				mid = i / float(key_width)
				linear.add_color_stop_rgba(mid-dt,  r,g,b,a*0.34)
				linear.add_color_stop_rgba(mid-(dt-0.001), r,g,b,a*0.8)
				linear.add_color_stop_rgba(mid+(dt-0.001), r,g,b,a*0.8)
				linear.add_color_stop_rgba(mid+dt, r,g,b,a*0.34)
			context.set_source(linear)
			context.fill_preserve()
			context.set_line_width(key_border_width)
			context.set_source_rgba(*key_border_color)
			context.stroke()
			
			# Draw the label
			context.select_font_face(
				label_style.get_font(),
				label_style.get_cairo_font_style(),
				label_style.get_cairo_font_weight(),
			)
			context.set_font_size( label_style.get_float("font-size") )
			
			x_bearing, y_bearing, width, height = context.text_extents(series.title)[:4]
			
			context.move_to(label_left - x_bearing, y - height / 2 - y_bearing)
			context.set_source_rgba(*label_style.get_color("color"))
			context.show_text(self.dashed_name)
		
		context.restore()