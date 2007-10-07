"""
Simplish interface to parts of the Last.fm API.
Has a built-in lock to stop requests happening at more than one per second.
"""

import os
import time

# Import [c]ElementTree
try:
	import cElementTree as ET
except:
	import elementtree.ElementTree as ET

# The directory to use to cache downloaded xml
cachedir = "/var/tmp/lastfm/"

# The lockfile to use to stop too many requests.
lockfile = os.path.join(cachedir, "netlock")
if not os.path.exists(lockfile):
	open(lockfile, "w")

# The Last.fm API url
lastfm_api_url = "http://ws.audioscrobbler.com/1.0/%s"

# Create the cache dir if we can
try:
	os.makedirs(cachedir)
except OSError:
	pass


def fetch(path, delay=1.0):
	"""Fetches the given path from the Last.fm API, 
	using a lock file to make sure that there's no more than 1 request a second.
	Will block until the URL is downloaded."""
	
	# Wait for the lock to pass
	lockvalue = open(lockfile).read().strip()
	while os.path.exists(lockfile) and lockvalue and (time.time() - float(lockvalue) < delay):
		time.sleep(0.001)
	
	# Write our own lock
	fo = open(lockfile, "w")
	fo.write(str(time.time()))
	fo.close()
	
	# Get the requested file
	import urllib
	return urllib.urlopen(lastfm_api_url % path)



def available_weeks(username):
	"""Returns a list of integer tuples, representing the
	available weeks for charts."""
	
	# Get and parse the XML
	root = ET.fromstring(fetch("user/%s/weeklychartlist.xml" % username).read())
	
	# Check the type
	assert root.tag == "weeklychartlist", "This is not a Weekly Chart List"
	
	# For each week, get the times
	weeks = []
	for tag in root.findall("chart"):
		start = float(tag.attrib['from'])
		end = float(tag.attrib['to'])
		weeks.append((start, end))
	
	return weeks



def track_chart(username, start, end):
	"""Retrieves the track chart for a single week.
	The data is returned as an ordered list of (trackname, artist, plays) tuples.
	Implements caching of the XML."""
	
	# Get the XML if it doesn't already exist
	filename = os.path.join(cachedir, "trackchart-%s-%s-%s.xml" % (username, start, end))
	if not os.path.exists(filename):
		fo = fetch("user/%s/weeklytrackchart.xml?from=%i&to=%i" % (username, start, end))
		import shutil
		shutil.copyfileobj(fo, open(filename, "w"))
	
	# Load and parse the XML
	tree = ET.parse(filename)
	root = tree.getroot()
	
	# Check the type
	assert root.tag == "weeklytrackchart", "This is not a Weekly Chart List"
	
	# Now, loop over the tracks
	tracks = []
	for tag in root.findall("track"):
		artist_tag = tag.find("artist")
		artist_name = artist_tag.text
		
		name = tag.find("name").text
		plays = int(tag.find("playcount").text)
		
		tracks.append((name, artist_name, plays))
	
	return tracks



def artist_chart(username, start, end):
	"""Retrieves the track chart for a single week.
	The data is returned as an ordered list of (artist, plays) tuples.
	Implements caching of the XML."""
	
	# We use the track data as it might already be cached
	tracks = track_chart(username, start, end)
	artists = {}
	
	for track, artist, plays in tracks:
		artists[artist] = artists.get(artist, 0) + plays
	
	artists = artists.items()
	artists.sort(key=lambda (x,y):y)
	artists.reverse()
	
	return artists



def artist_range_chart(username, start, end, callback=lambda x:x, dated=False):
	"""Like artist_chart, but aggregates over several weeks' charts into a list of values."""
	
	weeks = available_weeks(username)
	artist_totals = {}
	artists = {}
	
	matching_weeks = [(week_start, week_end) for week_start, week_end in weeks if (week_end > start) and (week_start < end)]
	i = 0
	
	for week_start, week_end in matching_weeks:
		for artist, plays in artist_chart(username, week_start, week_end):
			artist_totals[artist] = artist_totals.get(artist, 0) + plays
		i += 1.0 / len(matching_weeks)
		callback(i/2.0)
	
	artists = dict([(artist, []) for artist in artist_totals])
	for week_start, week_end in matching_weeks:
		plays = dict(artist_chart(username, week_start, week_end))
		for artist in artists:
			if dated:
				artists[artist].append((week_start, plays.get(artist, 0)))
			else:
				artists[artist].append(plays.get(artist, 0))
		i += 1.0 / len(matching_weeks)
		callback(i/2.0)
	
	artists = artists.items()
	artists.sort(key=lambda (x,y):y)
	artists.reverse()
	
	return artists