#!/usr/bin/python

import sys
import random
from graphication.output import FileOutput
from graphication.wavegraph import WaveGraph
from graphication.label import Label
from graphication.series import MultiSeries, SubSeries


class ColourLoop(object):
	def __init__(self, colours):
		self.colours = colours
	def __iter__(self):
		while 1:
			yield self.pop()
	def pop(self):
		self.colours = self.colours[1:] + self.colours[:1]
		return self.colours[-1]


# Read in the data
filename = sys.argv[1]
fo = open(filename)
labels = [x.strip() for x in fo.readline().split(",")]
data = []
for line in fo:
	data.append([int(x.strip()) for x in line.split(",")])

mseries = MultiSeries(range(len(data)))
series = zip(*data)
colours = ColourLoop(["#336699", "#669933", "#993366", "#996633"])

for i in range(len(labels)):
	label = labels[i]
	mseries.add_series(SubSeries(label, series[i], colours.pop()))

# Initialise our Style
from graphication.style import Style
style = Style()
style['wavegraph:dimming_top'] = 20
style['label:align'] = "left"
style['label:color'] = "#222"
style['default:font'] = "NeoSansLight"
style['label:font'] = "NeoSansNormal"

# Create the output
output = FileOutput(style)

# We'll have major lines every integer, and minor ones every half
labels = dict([(x, str(x)) for x in range(len(data))])

# OK, render that.
wg = WaveGraph(mseries, style, labels, True)
lb = Label(filename, style)

output.add_item(lb, x=10, y=5, width=490, height=20)
output.add_item(wg, x=0, y=30, width=500, height=200)

# Save the images
output.write("svg", "%s.svg" % filename)
output.write("png", "%s.png" % filename)
output.write("pdf", "%s.pdf" % filename)