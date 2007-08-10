
from setuptools import setup, find_packages
from graphication import release

setup(
	name = release.product,
	version = release.version,
	packages = find_packages(),
	description = "A Cairo-based graphing library",
	author = "Andrew Godwin",
	author_email = "graphication@aeracode.org",
	url = "http://aeracode.org/projects/graphication/",
	license = "GPL",
)