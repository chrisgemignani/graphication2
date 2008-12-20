
import sys
import math

import cairo

from graphication import default_css, Series
from graphication.text import text_bounds
from graphication.color import hex_to_rgba
from graphication.scales import SimpleScale, VerticalWavegraphScale
from graphication.barchart import BarChart

class CurvyBarChart(BarChart):
	
	def __init__(self, series_set, scale, style=None, vertical_scale=None, zero_base=True, label_on=True, stacked=True, sharp_edges=True, top_only=False, border_only=False):
		
		"""
		Constructor; creates a new CurvyBarChart.
		"""
		
		self.series_set = series_set
		self.style = default_css.merge(style)
		self.scale = scale
		self.label_height = style['curvybarchart label'].get_float("height", 30)
		self.label_on = label_on
		self.zero_base = zero_base
		self.stacked = stacked
		self.sharp_edges = sharp_edges
		self.top_only = top_only
		self.border_only = border_only
		
		if vertical_scale is None:
			if stacked:
				y_min, y_max = self.stacked_value_range()
			else:
				y_min, y_max = self.series_set.value_range()
			if self.zero_base:
				y_min = 0
			vertical_scale = VerticalWavegraphScale(y_min, y_max)
		self.y_scale = vertical_scale
	
	
	def calc_plot_size(self):
		self.plot_height = self.height - self.label_height
		self.plot_width = self.width
		self.plot_left = 0
		self.plot_top = 0
	
	
	def get_vertical_scale(self):
		return self.y_scale
	
	
	def draw_rounded_bar(self, context, x, y, w, h, top, bottom):
		r = w / 2.0
		rt = r * top
		rb = r * bottom
		
		if not self.sharp_edges:
			x = int(x)
			w = math.ceil(w)
		
		# Draw rounded rectangle
		context.move_to(x, y+rt)
		
		context.arc(x+rt, y+rt, rt, -math.pi, -math.pi/2.0)
		context.line_to(x+w-rt, y)
		context.arc(x+w-rt, y+rt, rt, -math.pi/2.0, 0)
		
		context.line_to(x+w, y+h-rb)
		
		context.arc(x+w-rb, y+h-rb, rb, 0, math.pi/2.0)
		context.line_to(x+rb, y+h)
		context.arc(x+rb, y+h-rb, rb, math.pi/2.0, math.pi)
		
		context.line_to(x, y+rt)
	
	
	def render(self, context, debug=False):
		
		context.save()
		
		### Draw the bars
		# Get width per bar block
		keys = self.series_set.keys()
		per_bar = float(self.plot_width) / len(keys)
		# Some more drawing parameters
		zero_line = self.plot_top + self.plot_height
		bar_style = self.style["curvybarchart bar"]
		label_style = self.style["curvybarchart label"]
		bar_padding = bar_style.get_float("padding")
		bar_padding_top = bar_style.get_float("padding-top")
		border_width = bar_style.get_float("border-width")
		border_color = bar_style.get_color("border-color")
		# Get the list of 'lines' we'll use for labels
		lines = {}
		for linepos, title, ismajor in self.scale.get_lines():
			lines[linepos] = title
		# Draw the bars at each location
		left = self.plot_left
		for key in keys:
			stack = self.series_set.stack(key)
			bottom = zero_line
			inner_left = 0
			
			def draw_series():
				height = 0 - self.y_scale.get_point(value) * self.plot_height
				x, y, w, h = (
					left + inner_left + bar_padding,
					bottom,
					per_bar / (self.stacked and 1 or len(stack)) - bar_padding*2,
					height + bar_padding_top,
				)
				y, h = y + h, abs(h)
				# Set stroke width
				bwidth = bar_style.get_float("border-width", 0)
				context.set_line_width(bwidth)
				# If we're only drawing the top, just draw it
				if self.top_only:
					context.set_source_rgba(*series.color_as_rgba())
					context.move_to(x, y)
					context.line_to(x+w, y)
					context.stroke()
					return
				if height:
					self.draw_rounded_bar(
						context,
						x, y, w, h,
						bar_style.get_float('curve-top'),
						bar_style.get_float('curve-bottom'),
					)
					# Fill it with the right colour
					if not self.border_only:
						context.fill()
					# Stroke round it
					self.draw_rounded_bar(
						context,
						x + bwidth/2.0, y + bwidth/2.0, w - bwidth, h - bwidth,
						bar_style.get_float('curve-top'),
						bar_style.get_float('curve-bottom'),
					)
					if self.border_only:
						context.set_source_rgba(*series.color_as_rgba())
					else:
						context.set_source_rgba(*bar_style.get_color("border-color", "#0000"))
					context.stroke()
				# Draw numeric label on bar if req'd
				if self.label_on:
					context.select_font_face(
						bar_style.get_font(),
						bar_style.get_cairo_font_style(),
						bar_style.get_cairo_font_weight(),
					)
					context.save()
					label = ("%." + str(bar_style.get_int("value-accuracy")) + "f") % value
					context.set_font_size(bar_style.get_float("font-size"))
					x_bearing, y_bearing, twidth, theight = context.text_extents(label)[:4]
					cx = x + w/2.0
					context.set_source_rgba(*bar_style.get_color("color"))
					
					# See if we need to put the label above the bar coz it's too small
					label_padding =  bar_style.get_float("padding-bottom")
					if theight + 2*label_padding > h:
						h = 0
						context.set_source_rgba(*bar_style.get_color("color-secondary", bar_style.get_color("color")))
					
					context.move_to(
						cx - twidth / 2 - x_bearing,
						y + h - label_padding,
					)
					
					context.set_font_options(bar_style.get_cairo_font_options())
					
					context.show_text(label)
					context.fill()
					context.restore()
				
			if self.stacked:
				value = sum([v for s,v in stack])
				height = self.y_scale.get_point(value) * self.plot_height
				linear = cairo.LinearGradient(0, self.plot_height - height, 0, self.plot_height)
				prog = 1
				for series, svalue in stack:
					if svalue:
						pc = svalue / float(value)
						linear.add_color_stop_rgba(prog,  *series.color_as_rgba())
						prog -= pc
						linear.add_color_stop_rgba(prog+0.001,  *series.color_as_rgba())
				context.set_source(linear)
				draw_series()
				inner_left += per_bar
			else:
				for series, value in stack:
					context.set_source_rgba(*series.color_as_rgba())
					draw_series()
					inner_left += per_bar / len(stack)
			
			# Draw label part
			# Draw rounded label bar bit
			label_margin = label_style.get_float("margin-top")
			x, y = left + bar_padding, self.plot_height + label_margin
			w, h = per_bar - bar_padding*2, self.label_height - label_margin
			self.draw_rounded_bar(
				context,
				x, y,
				w, h,
				label_style.get_float('curve-top'),
				label_style.get_float('curve-bottom'),
			)
			if self.scale.is_secondary(key):
				context.set_source_rgba(*label_style.get_color("background2-color", label_style.get_color("background-color")))
			else:
				context.set_source_rgba(*label_style.get_color("background-color"))
			context.fill()
			# Draw text
			context.select_font_face(
				label_style.get_font(),
				label_style.get_cairo_font_style(),
				label_style.get_cairo_font_weight(),
			)
			context.set_font_options(label_style.get_cairo_font_options())
			label = self.scale.label_for(key)
			labels = label.split("\n")
			size = label_style.get_float("font-size")
			bh = size * label_style.get_float("line-height")
			by = y + bh + label_style.get_float("padding-top")
			cx = x + w/2.0
			for label in labels:
				context.set_font_size(size)
				x_bearing, y_bearing, width, height = context.text_extents(label)[:4]
				context.move_to(cx - width / 2 - x_bearing, by)
				context.set_source_rgba(*label_style.get_color('color'))
				context.show_text(label)
				context.fill()
				by += bh
			
			left += per_bar
		
		# Debug: outlines plot area
		#context.set_source_rgba(255,255,255,255)
		#context.rectangle(0, 0, self.width, self.plot_height)
		#context.stroke()
		
		context.restore()

class TooClose(Exception): pass
