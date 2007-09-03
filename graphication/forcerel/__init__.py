
import math
import cairo
import random
from graphication.color import hex_to_rgba
from graphication.scales import SimpleScale

class ForceRelPlot(object):
	
	"""
	Plots a NodeSet with the primary axis up the graph.
	The nodes are arranged so they are force-separated.
	"""
	
	def __init__(self, nodeset, style, scale):
		
		self.nodeset = nodeset
		self.style = style
		self.y_scale = scale
		self.force_separate()
	
	
	def force_separate(self):
		
		# Randomise the starting positions a bit
		for node in self.nodeset:
			node.left = random.random() - 0.5
		
		gr = 3
		sp = 3
		
		for i in range(50):
			self.force_iterate(0.1)
	
	
	def force_iterate(self, dt):
		"""Performs one force-sep step."""
		
		linkforce = 3
		sepforce = 3
		
		# Collect the positions of each node for force calcs
		for node in self.nodeset:
			node.old_left = node.left
		
		# Do spring calcs on the links
		for link in self.nodeset.links:
			
			# dy is the vertical distance, dist is the length of the link
			dy = abs(link.start.value - link.end.value)
			dx = link.start.left - link.end.left
			dist = (dy**2 + dx**2)**0.5
			
			# Work out how much it's 'stretched', and apply a 'force'
			if dy == 0:
				stretch = dist
			else:
				stretch = dist / dy
			force = (stretch ** 2) * linkforce
			
			link.start.left -= (dx / 2.0) * (force * dt)
		
		# Repel the nodes from each other
		for node in self.nodeset:
			for other_node in self.nodeset:
				if node is not other_node:
					dx = node.old_left - other_node.old_left
					dy = node.value - other_node.value
					dist = (dx**2 + dy**2)**0.5
					force = sepforce / ((dist + 0.5) ** 2)
					other_node.left += dx * force * dt
	
	
	def set_size(self, width, height):
		
		# First, store the width and height
		self.width = width
		self.height = height
		
		# Get extent of x axis
		min_left, max_left = 0, 0
		for node in self.nodeset:
			min_left = min(node.left, min_left)
			max_left = max(node.left, max_left)
		
		# Create a scale and work out x positions
		self.x_scale = SimpleScale(min_left,max_left,1,0.5)
		for node in self.nodeset:
			node.x = self.x_scale.get_point(node.left)
	
	
	def render(self, context):
		
		context.save()
		
		major_style = self.style['forcerel grid.major']
		minor_style = self.style['forcerel grid.minor']
		
		plot_left = 0
		
		# Render the labels first
		for linepos, title, ismajor in self.y_scale.get_lines():
			
			if ismajor:
				this_style = major_style
			else:
				this_style = minor_style
			
			label_style = this_style.sub('label')
			
			context.select_font_face(
				label_style.get_font(),
				label_style.get_cairo_font_style(),
				label_style.get_cairo_font_weight(),
			)
			context.set_font_size( label_style.get_float("font-size") )
			
			y = linepos * self.height
			x_bearing, y_bearing, width, height = context.text_extents(title)[:4]
			padding = label_style.get_float("padding")
			left = padding - x_bearing
			
			context.move_to(left - x_bearing, y - height / 2.0 - y_bearing)
			context.show_text(title)
			
			plot_left = max(left + width + padding, plot_left)
		
		
		# Then the lines
		for linepos, title, ismajor in self.y_scale.get_lines():
			
			if ismajor:
				this_style = major_style
			else:
				this_style = minor_style
			
			line_style = this_style.sub('line')
			
			context.set_line_width(line_style.get_float("width"))
			context.set_source_rgba(*line_style.get_color("color"))
			
			y = linepos * self.height
			context.move_to(plot_left, y)
			context.line_to(self.width, y)
			context.stroke()
		
		
		plot_width = self.width - plot_left
		
		# Work out node locations
		for node in self.nodeset:
			node.x = node.x * plot_width + plot_left
			node.y = self.y_scale.get_point(node.value) * self.height
		
		
		# Draw the links
		for link in self.nodeset.links:
			context.set_source_rgba(*hex_to_rgba(link.color))
			context.move_to(link.start.x, link.start.y)
			context.line_to(link.end.x, link.end.y)
			context.stroke()
		
		
		# Draw nodes
		r = self.style['forcerel point'].get_float("radius")
		for node in self.nodeset:
			
			context.set_source_rgba(*hex_to_rgba(node.color))
			
			context.move_to(node.x, node.y-r)
			context.arc(node.x, node.y, r, 0, math.pi * 2)
			context.fill()