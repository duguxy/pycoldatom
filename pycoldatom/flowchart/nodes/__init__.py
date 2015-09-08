"""
In order to be imported into node library, a .py file should:
- endswith 'Node'
- contain a global variable nodelist, which is a list object with all the node class to be imported
"""

import os
import importlib
import traceback
import logging

logger = logging.getLogger('flowchart')
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
			logger.info('Module %s loaded' % modname)
	except Exception as e:
		logger.error(traceback.format_exc())