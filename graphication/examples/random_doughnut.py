#!/usr/bin/python

import random
from graphication import FileOutput, Series, SeriesSet, Label, SimpleScale, css
from graphication.doughnut import Doughnut

colours = ["#844648","#b3c234","#244574"]

series_set = SeriesSet()
for i in range(3):
	series_set.add_series(Series(
		"Series%s" % i,
		{0: random.randint(1,100)},
		colours[i%3]
	))

# Initialise our style
css.install_hook()
import graphication.default_css as style

# Create the output
output = FileOutput(style, 5)

# OK, render that.
dn = Doughnut(series_set, style)
lb = Label("Test Graph", style)

output.add_item(dn, x=0, y=0, width=300, height=300)

# Save the images
output.write("png", "dn.png")
output.write("pdf", "dn.pdf")