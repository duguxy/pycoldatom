from pyqtgraph.flowchart import Node
import numpy as np
import inspect
from scipy.ndimage.filters import median_filter
from ...utils.qt import setBusyCursor, recoverCursor

def nodeFuncWrapper(func, nodename=None, paths=[('functions',)], interm=None, outterm=['output'], paras={}, cpuheavy=False):
	if nodename is None:
		nodename = func.__name__

	if interm is None:
		try:
			interm = inspect.getfullargspec(func)[0]
		except:
			interm = ['input']

	terminals = {}
	terminals.update({name: {'io':'in'} for name in interm})
	terminals.update({name: {'io':'out'} for name in outterm})

	class FuncNode(Node):
		nodeName = nodename
		nodePaths = paths

		def __init__(self, name):
			super().__init__(name, terminals=terminals)
			self.func = func

		def process(self, **kwargs):
			args = [kwargs[i] for i in interm]
			if cpuheavy:
				self.statusBar.showMessage('Processing %s...' % self.name())
				setBusyCursor()
				try:
					result = self.func(*args, **paras)
				finally:
					recoverCursor()
					self.statusBar.clearMessage()
			else:
				result = self.func(*args, **paras)

			if len(outterm) == 1:
				return {outterm[0]: result}
			else:
				return dict(zip(outterm, result))

	return FuncNode

nodelist = []
for f in [np.exp, np.log]:
	nodelist.append(nodeFuncWrapper(f, paths=[('Math',)]))

for f in [np.add, np.subtract, np.divide, np.multiply]:
	nodelist.append(nodeFuncWrapper(f, paths=[('Math',)], interm=['x1', 'x2']))

for name, paras in zip(['sum', 'sumX', 'sumY'], [{}, {'axis':0}, {'axis':1}]):
	nodelist.append(nodeFuncWrapper(np.sum, nodename=name, paths=[('Analysis',)], interm=['input'], paras=paras))

def calculateOD(sig, ref, bkg):
	od = -np.log((sig-bkg) / (ref-bkg))
	bad = np.logical_or(np.isinf(od), np.isnan(od))
	od[bad] = 0.0
	return od

calculateODNode = nodeFuncWrapper(calculateOD, nodename='OD', paths=[('Analysis',)])
nodelist.append(calculateODNode)