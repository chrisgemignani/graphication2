
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
		
		# Draw gridlines
		context.set_line_width(self.style['forcerel:grid_major_width'])
		context.set_source_rgba(*hex_to_rgba(self.style['forcerel:grid_major_color']))
		
		# Get lines, and setup label params
		lines = list(self.y_scale.get_lines())
		max_label_width = 0
		pad_left = self.style['forcerel:left_label_padding']
		pad_right = self.style['forcerel:right_label_padding']
		context.select_font_face(self.style['forcerel:label_font'], cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		context.set_font_size(self.style['forcerel:label_size'])
		
		# Draw labels
		for line, title, ismajor in lines:
			y = line * self.height
			
			x_bearing, y_bearing, width, height = context.text_extents(title)[:4]
			context.move_to(pad_left - x_bearing, y - height / 2.0 - y_bearing)
			context.show_text(title)
			
			max_label_width = max(width + x_bearing, max_label_width)
		
		
		# Draw the gridlines
		plot_left = max_label_width + pad_left + pad_right
		plot_width = self.width - plot_left
		
		for line, title, ismajor in lines:
			y = line * self.height
			
			context.move_to(plot_left, y)
			context.line_to(self.width, y)
			context.stroke()
		
		
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
		r = self.style['forcerel:point_radius']
		for node in self.nodeset:
			
			context.set_source_rgba(*hex_to_rgba(node.color))
			
			context.move_to(node.x, node.y-r)
			context.arc(node.x, node.y, r, 0, math.pi * 2)
			context.fill()