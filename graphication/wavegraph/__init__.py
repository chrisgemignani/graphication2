
from graphication.color import hex_to_rgba

from graphication.wavegraph.curves import WaveGraphCurves
from graphication.wavegraph.grid import WaveGraphVGrid
from graphication.wavegraph.text import WaveGraphCurveLabels, WaveGraphAxisLabels

class WaveGraph(object):
	
	
	def __init__(self, mseries, style, x_labels={}, label_curves=False, vertical_axis=False):
		
		"""
		Constructor; creates a new WaveGraph.
		
		@param mseries: The data to plot, as a MultiSeries
		@type mseries: graphication.series.MultiSeries
		
		@param style: The Style to apply to this graph
		@type style: graphication.style.Style
		
		@param x_labels: A dict specifying where to draw labels along the bottom axis. A dict; keys are x-positions, values are label text. If there value is None, draws a minor gridline.
		@type x_labels: dict
		
		@param label_curves: If the curves should have labels written directly on top of them, fitted into their shape. Note: Takes a while to render.
		@type label_curves: bool
		
		@param vertical_axis: If a vertical scale should be drawn on the graph
		@type vertical_axis: bool
		"""
		
		self.style = style
		
		self.curves = WaveGraphCurves(mseries, yoffset=self.style['wavegraph:vertical_center'], vextent=self.style['wavegraph:vertical_extent'])
		
		# Sort the labels into minor and major
		x_lines_minor, x_labels_major = [], {}
		for x, text in x_labels.items():
			if text is None:
				x_lines_minor.append(x)
			else:
				x_labels_major[x] = str(text)
		
		# Create the minor grid if needed
		if x_lines_minor:
			self.grid_minor = WaveGraphVGrid(self.curves, x_lines_minor)
		else:
			self.grid_minor = None
		
		# And the major grid
		if x_labels_major:
			self.grid_major = WaveGraphVGrid(self.curves, x_labels_major.keys())
			self.x_labels_major = WaveGraphAxisLabels(self.curves, x_labels_major)
		else:
			self.grid_major = None
			self.x_labels_major = None
	
	
	def set_size(self, width, height):
		
		# First store the basic widths
		self.width = width
		self.height = height
		
		# Do we need space on the left for a scale?
		self.cwidth = self.width
		
		# Do we need space on the bottom for labels?
		if self.x_labels_major:
			self.cheight = self.height - self.style['wavegraph:label_size'] * 3
		else:
			self.cheight = self.height
		
		# Set the various sizes
		self.curves.set_size(self.cwidth, self.cheight)
		
		if self.grid_minor:
			self.grid_minor.set_size(self.cwidth, self.cheight)
		
		if self.grid_major:
			self.grid_major.set_size(self.cwidth, self.cheight)
		
		if self.x_labels_major:
			self.x_labels_major.set_size(self.cwidth, self.style['wavegraph:label_size'] * 3)
	
	
	def render(self, context):
		
		if self.grid_minor:
			self.grid_minor.render(context,
				color=self.style['wavegraph:grid_minor_color'],
				thickness=self.style['wavegraph:grid_minor_width'],
			)
		
		if self.grid_major:
			self.grid_major.render(context,
				color=self.style['wavegraph:grid_major_color'],
				thickness=self.style['wavegraph:grid_major_width'],
			)
		
		self.curves.render(context,
			smooth=self.style['wavegraph:smoothness'],
		)
		
		if self.x_labels_major:
			context.save()
			context.translate(0, self.cheight)
			self.x_labels_major.render(context,
				color=self.style['wavegraph:label_color'],
				size=self.style['wavegraph:label_size'],
				font=self.style['wavegraph:label_font'],
			)
			context.restore()