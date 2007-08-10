#!/usr/bin/python

import random
from graphication.output import FileOutput
from graphication.wavegraph import WaveGraph
from graphication.series import MultiSeries, SubSeries

# Create a random multiseries
num_points = 10
randomvalues = lambda n: [random.choice(range(2,25)) for i in range(n)]
mseries = MultiSeries(range(num_points))
for i in range(6):
	mseries.add_series(SubSeries("Series%s" % i, randomvalues(num_points), "#3366%2xff" % (50*i)))

# Initialise our Style
from graphication.style import Style
style = Style()

# Create the output
output = FileOutput(style)

# We'll have major lines every integer, and minor ones every half
labels = dict([(x, str(x)) for x in range(num_points)])
labels.update(dict([(x+0.5, None) for x in range(num_points-1)]))

# OK, render that.
wg = WaveGraph(mseries, style, labels)
output.add_item(wg, x=0, y=30, width=800, height=300)

# Save the images
output.write("svg", "test.svg")
output.write("png", "test.png")