
from graphication import default_css
from colorsys import rgb_to_hsv, hsv_to_rgb


def rgb_to_hex(r, g, b):
	return "#%2x%2x%2x" % (r*255, g*255, b*255)


def hsv_to_hex(h, s, v):
	return rgb_to_hex(*hsv_to_rgb(h, s, v))


def interleave(l):
	nl = []
	append = True
	for x in l:
		if append:
			nl.append(x)
		else:
			nl = [x] + nl
		append = not append
	return nl


def uninterleave(l):
	i = 0
	plus = True
	n = len(l)
	m = n / 2
	nl = []
	for i in range(m):
		nl.append(l[i])
		nl.append(l[-(i+1)])
	if n % 2:
		nl.append(l[m])
	nl.reverse()
	return nl


class Colourer(object):
	
	"""A colourer takes a SeriesSet and colours the
	series in nicely to be shown in a wavegraph."""
	
	
	def __init__(self, style=None):
		
		self.style = default_css.merge(style)
	
	
	def colour(self, series_set):
		
		style = self.style['colourer']
		
		start_rgb = style.get_color('gradient-start', "#334489")[:3]
		end_rgb = style.get_color('gradient-end', "#2d8f3c")[:3]
		
		start_hsv = rgb_to_hsv(*start_rgb)
		end_hsv = rgb_to_hsv(*end_rgb)
		hue, sat, val = start_hsv
		
		hue_delta = (end_hsv[0] - start_hsv[0]) / len(series_set)
		satvalcycle = [(.68, .47), (.53, .55), (.60, .63), (.50, .50), (.72, .65), (.63, .55), (.75, .56)]
		sat, val = satvalcycle[0]
		
		for series in uninterleave(list(series_set)):
			series.color = hsv_to_hex(hue, sat, val)
			hue += hue_delta
			if hue > 1 or hue < 0:
				hue %= 1
			satvalcycle = satvalcycle[1:] + satvalcycle[:1]
			sat, val = satvalcycle[0]