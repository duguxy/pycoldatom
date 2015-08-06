from types import ModuleType
import importlib

def rreload(module, ignore=set('_imp')):
	"""Recursively reload modules."""
	importlib.reload(module)
	for attribute_name in dir(module):
		attribute = getattr(module, attribute_name)
		if type(attribute) is ModuleType and attribute.__name__ not in ignore:
			ignore.add(attribute.__name__)
			rreload(attribute, ignore)