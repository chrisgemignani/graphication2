#!/usr/bin/python

import random
from graphication import FileOutput, Node, NodeSet, NodeLink, Label, SimpleScale, css
from graphication.forcerel import ForceRelPlot

# Create the NodeSet, and add some nodes to it
nodeset = NodeSet()

n = 30

for i in range(n):
	node = Node(random.choice(range(10)))
	nodeset.add_node(node)

# Add some test links
for i in range(20):
	nodeset.add_link(NodeLink(random.choice(nodeset.nodes), random.choice(nodeset.nodes)))

# Make a scale
value_min, value_max, value_range = nodeset.value_range()
scale = SimpleScale(value_min, value_max, 1, 1)

# Initialise our Style
css.install_hook()
import graphication.default_css as style

# Create the output
output = FileOutput(style)

# OK, render that.
forcerel = ForceRelPlot(nodeset, style, scale)

output.add_item(forcerel, x=0, y=0, width=200, height=600)

# Save the images
#output.write("svg", "forcerel.svg")
#output.write("png", "forcerel.png")
output.write("pdf", "forcerel.pdf")