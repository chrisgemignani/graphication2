"""
Graphication, the pretty Python graphing library.

Copyright Andrew Godwin 2007
$Id$
"""


import graphication.css as css
css.install_hook()
from graphication import default_css

from graphication.output import FileOutput
from graphication.label import Label
from graphication.series import Series, SeriesSet, Node, NodeSet, NodeLink
from graphication.scales import SimpleScale
from graphication.scales.date import DateScale, AutoDateScale