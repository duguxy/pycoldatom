import os
import importlib
import traceback

path = os.path.dirname(os.path.abspath(__file__))
nodelist = []
for filename in os.listdir(path):
	modname, ext = os.path.splitext(filename)
	if not (ext=='.py' and modname.endswith('Node')):
		continue	

	try:
		mod = importlib.import_module('.%s' % modname, __package__)
		mod = importlib.reload(mod)
		nodename = modname[0].upper() + modname[1:]
		if hasattr(mod, 'nodelist'):
			nodelist.extend(mod.nodelist)
			print('Module %s loaded' % modname)
	except Exception as e:
		print(traceback.format_exc())