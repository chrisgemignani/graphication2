#!/usr/bin/python

import sys
import time
import random
import graphication.lastfm as lastfm
from graphication import FileOutput, Series, SeriesSet, Label, SimpleScale, css
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
css.install_hook()
import graphication.examples.lastfm_css as style

# Create the output
output = FileOutput(style)

# We'll have major lines every integer, and minor ones every half
scale = SimpleScale(time.time() - 31557600, time.time(), 86400*7)

# OK, render that.
wg = WaveGraph(series_set, scale, style, True)
lb = Label(username, style)

output.add_item(lb, x=10, y=5, width=490, height=20)
output.add_item(wg, x=0, y=30, width=30*len(series_set.keys()), height=200)

# Save the images
output.write("pdf", "%s.pdf" % username)