"""
graphication.css:

  A lightweight, simplified-CSS parser and matcher.

Implements element-, id- and class-based selecting/matching.
All properties inherit by default, and there's no support for the 'inherit' keyword.

Any @media, @import, etc. parts are also entirely useless. As is !important.

Copyright Andrew Godwin, 2007
Released under the terms of the GPL, version 3.

$Id$
"""

import re
from UserDict import UserDict

def selector_split(string, single_class=True):
	
	"""
	Turns a selector-ish string into a list of (tag, id, class) tuples.
	If single_class is False, class is a list of classes rather than a string.
	
	@param string: The seleector string to parse.
	@type string: str
	
	@param single_class: Whether to return lists of classes (False) or a single class (True).
	@type single_class: bool
	"""
	
	bits = string.split()
	details = []
	
	for bit in bits:
		if "#" in bit:
			tag, idcls = bit.split("#", 1)
			idcls = idcls.split(".")
			id = idcls[0]
			cls = idcls[1:]
		else:
			id = None
			tagcls = bit.split(".")
			tag = tagcls[0]
			cls = tagcls[1:]
	
		# Allow for tag wildcards
		if tag == "*":
			tag = None
		
		# Make sure we use None for non-existence
		tag = tag or None
		id = id or None
		
		if single_class:
			if len(cls):
				cls = cls[0]
			else:
				cls = None
		
		details.append((tag, id, cls))
	
	return details


class CssSelector(object):
	
	"""
	Represents a CSS selector, as well as performing useful selector-related
	tasks.
	"""
	
	def __init__(self, details):
		
		"""
		Constructor.
		
		@param details: The 'details' (list of (tag, id, class) tuples) to use.
		@type details: list
		"""
		
		# Details is a list of (element, id, class) tuples. One or more of each can be None.
		self.details = details
		self.calculate_specificity()
	
	
	def __repr__(self):
		return "<CssSelector %s>" % self.details
	
	
	def detail_to_str(self, detail):
		
		"""
		Turns a single detail into a part of a CSS textual selector.
		i.e. ("grid", None, "first") -> 'grid.first'
		
		@param detail: The detail to stringify
		@type detail: tuple
		"""
		
		s = detail[0] or "*"
		if detail[1]:
			s += "#" + detail[1]
		if detail[2]:
			s += "." + detail[2]
		return s
	
	
	def __str__(self):
		return " ".join(map(self.detail_to_str, self.details))
	
	
	@classmethod
	def from_string(self, string):
		
		"""
		Alternate constructor; initialises from a CSS selector string.
		
		@param string: The CSS selector string to initialise from.
		@type string: str
		"""
		
		details = selector_split(string, True)
		return self(details)
	
	
	def calculate_specificity(self):
		
		"""
		Caculates the specificity of this selector (see CSS spec for details).
		"""
		
		self.specificity = [0,0,0]
		for element, id, cls in self.details:
			if element is not None:
				self.specificity[1] += 1
			if id is not None:
				self.specificity[0] += 1
			if cls is not None:
				self.specificity[2] += 1
	
	
	def matches(self, element_rep):
		"""
		Sees if this selector matches the given 'element representation'.
		This is a list of (element, id, [classes]) tuples.
		
		@param element_rep: The element representation to match. 
		                    A list of (tag, id, [classes]) tuples.
		@type element_rep: list
		"""
		
		di = 0
		
		for element, id, clss in element_rep:
			curr_det = self.details[di]
			if curr_det[0] in [element, None]:
				if curr_det[1] in [id, None]:
					if curr_det[2] in clss + [None]:
						di += 1
						if di >= len(self.details):
							return True
		
		return di >= len(self.details)



class CssRule(object):
	
	"""
	Represents a single CSS rule.
	Has a selector, and a dictionary of properties.
	"""
	
	def __init__(self, selector, properties={}):
		
		"""
		Constructor.
		
		@param selector: The selector to use for this rule. You can pass 
		                 either a CSS selector string or a CssSelector.
		@type selector: str or CssSelector
		"""
		
		if isinstance(selector, str) or isinstance(selector, unicode):
			selector = CssSelector.from_string(selector)
		
		assert isinstance(selector, CssSelector), "The selector must be a CssSelector or a string."
		
		self.selector = selector
		self.properties = properties
	
	
	def __repr__(self):
		return "<CssRule; %i properties, selector %s>" % (len(self.properties), self.selector)



class CssProperties(UserDict):
	
	"""
	Like a dictionary, except it has things like get_int and get_list methods.
	"""
	
	
	def get_int(self, key, default):
		"""Like dict.get, but coerces the result to an integer."""
		return int(self.get(key, default))
	
	
	def get_list(self, key, default):
		"""Like dict.get, but splits the result as a comma-separated list."""
		return [x.strip() for x in self.get(key, default).split(",")]
	
	
	def get_align(self, key, default):
		"""Like dict.get, but always returns a number between 0 and 1.
		Correctly interprets 'top', 'left', 'middle', 'center', etc., as well
		as percentages."""
		val = self.get(key, default)
		
		# Try percentages or keywords
		if isinstance(val, str) or isinstance(val, unicode):
			if str[-1] == "%":
				val = float(str[:-1]) / 100.0
			else:
				val = {
					"left": 0.0,
					"top": 0.0,
					"middle": 0.5,
					"center": 0.5,
					"centre": 0.5,
					"bottom": 1.0,
					"right": 1.0,
				}[val]
		
		# Make sure it's valid
		try:
			val = float(val)
		except ValueError:
			raise ValueError("Invalid value for alignment key '%s': %s" % (key, val))
		
		assert (val >= 0) and (val <= 1), "Alignment key '%s' must have a value between 0 and 1, not %s." % (key, val)
		
		return val



class CssStylesheet(object):
	
	"""
	Contains none or more CssRules.
	You can add or remove rules, or pass in element names
	to see what properties it gets.
	"""
	
	def __init__(self):
		"""
		Constructor. Takes no arguments, initialises to an empty stylesheet.
		"""
		
		self.rules = []
	
	
	def add_rule(self, rule):
		"""
		Adds the given rule to the CssStylesheet.
		
		@param rule: The rule to add.
		@type rule: CssRule
		"""
		
		self.rules.append(rule)
		self.rules.sort(key=lambda r: r.selector.specificity)
	
	
	def get_properties(self, element):
		
		"""
		Returns the properties for the element 'element'.
		
		@param element: An element-list of (tag, id, [classes]) tuples
		@type element: list
		"""
		
		# To stop recursion, and also a sensible fallback
		if not element:
			return {}
		
		# Recurse to get inherited properties
		properties = self.get_properties(element[:-1])
		
		# Find matching rules (they're already in order of specificity)
		for rule in self.rules:
			if rule.selector.matches(element):
				properties.update(rule.properties)
		
		return CssProperties(properties)
	
	
	def get_properties_str(self, element_str):
		
		"""
		Returns the properties for the element 'element', using a selector-like
		shorthand syntax for the element.
		
		@param element: A CSS-selector like string (can have .multiple.classes)
		@type element: str
		"""
		
		element = selector_split(element_str, False)
		return self.get_properties(element)
	
	
	# Useful shorthand
	props = get_properties_str
	
	
	def update(self, stylesheet):
		
		"""
		Updates this stylesheet with rules from the other one, with the other
		stylesheet's rules taking preference.
		
		@param stylesheet: The stylesheet to update from.
		@type stylesheet: CssStylesheet
		"""
		
		# TODO: A more sophisticated update that removes duplicates.
		self.rules += stylesheet.rules
		self.rules.sort(key=lambda r: r.selector.specificity)
	
	
	def __repr__(self):
		return "<CssStylesheet; %i rules>" % len(self.rules)
	
	
	def __iter__(self):
		return iter(self.rules)
	
	
	@classmethod
	def from_css(cls, css):
		"""
		Alternate constructor; creates a CssStylesheet from a CSS string.
		
		@param css: The css stylesheet to parse.
		@type css: str
		"""
		
		self = cls()
		self.load_css(css)
		return self
	
	
	def load_css(self, css):
		"""
		Parses a CSS string and adds the rules it contains.
		
		@param css: The css stylesheet to parse.
		@type css: str
		"""
		
		# Initialise loop vars
		in_comment = in_declaration = False
		buffer = ""
		key = value = None
		
		# Read the css one character at a time
		while css:
			buffer += css[0]
			css = css[1:]
			
			# If we're not in a comment, do stuff
			if not in_comment:
				
				# Start a comment?
				if buffer[-2:] == "/*":
					in_comment = True
				
				# We might be outside a declaratin...
				elif not in_declaration:
					
					# Are we starting a declaration?
					if buffer[-1] == "{":
						selector = buffer[:-1].strip()
						properties = {}
						buffer = ""
						in_declaration = True
				
				# ...or outside one...
				elif in_declaration:
					
					# Are we ending here?
					if buffer[-1] == "}":
						value = buffer[:-1].strip()
						if key:
							properties[key] = value
						self.add_rule(CssRule(selector, properties))
						buffer = ""
						key = value = None
						in_declaration = False
					
					# Moving from a key to a value?
					elif buffer[-1] == ":":
						key = buffer[:-1].strip()
						buffer = ""
					
					# Ending a property?
					elif buffer[-1] == ";":
						value = buffer[:-1].strip()
						properties[key] = value
						buffer = ""
						key = value = None
			
			# All we can do is exit a comment.
			else:
				if buffer[-2:] == "*/":
					in_comment = False
					buffer = ""



class CssImporter(object):
	
	"""
	Magical importer for CSS files. Should be stuck in sys.meta_path.
	"""
	
	exts = [".css"]
	
	def find_module(self, fullname, path=None):
		
		import sys, os
		from os.path import isdir, join, exists, abspath
		
		name = fullname.split('.')[-1]
		
		# Get our paths
		paths = sys.path
		if path:
			paths = path + paths
		
		# Search 'em
		for path in paths:
			path = abspath(path)
			if isdir(path):
				path = join(path, name)
				for ext in self.exts:
					if exists(path + ext):
						self.filename = path + ext
						return self
		
		return None
	
	
	
	def load_module(self, fullname):
		stylesheet = CssStylesheet.from_css(open(self.filename).read())
		return stylesheet
	
	
	@classmethod
	def install(cls):
		"""Installs the import hook so that CSS files can be imported using the 'import' command."""
		import sys
		sys.meta_path.append(cls())
	
	
	@classmethod
	def uninstall(cls):
		"""Uninstalls the import hook."""
		import sys
		sys.meta_path = [x for x in sys.meta_path if not isinstance(x, cls)]


def install_hook():
	"""Installs the import hook."""
	CssImporter.install()