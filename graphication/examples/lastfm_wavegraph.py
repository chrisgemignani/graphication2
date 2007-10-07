#!/usr/bin/python

import sys
import time
import random
import graphication.lastfm as lastfm
from graphication import *
from graphication.wavegraph import WaveGraph

# Grab the last year's worth for the given username
username = sys.argv[1]
def p(x): print "%3.0f%% complete" % (x*100,)
artists = lastfm.artist_range_chart(username, time.time() - 31557600, time.time(), callback=p, dated=True)

# Create the series set and throw in the artists

series_set = SeriesSet()
for artist, plays in artists:
	series_set.add_series(Series(
		artist,
		dict(plays),
	))

# Initialise our style
import graphication.examples.lastgraph_css as style

# Colour that set!
cr = Colourer(style)
cr.colour(series_set)

# Create the output
output = FileOutput(style)

# Weeky scale
scale = AutoWeekDateScale(series_set)

# OK, render that.
wg = WaveGraph(series_set, scale, style, label_curves=True)
lb = Label(username, style)

width = 30*len(series_set.keys())
output.add_item(lb, x=10, y=5, width=width-20, height=20)
output.add_item(wg, x=0, y=30, width=width, height=200)

# Save the images
output.write("pdf", "%s.pdf" % username)