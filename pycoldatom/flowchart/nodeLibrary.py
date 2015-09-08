import pyqtgraph.flowchart.NodeLibrary as pgfcnl
from ..utils.rreload import rreload

class NodeLibrary(pgfcnl.NodeLibrary):
	"""NodeLibrary supporting recursively reload"""
	
	def __init__(self):
		super().__init__()
		self.nodes = None
		self.reload()

	def reload(self):
		from . import nodes
		if self.nodes is None:
			self.nodes = nodes
		else:
			rreload(nodes)

		for n in nodes.nodelist:
			self.addNodeType(n, n.nodePaths, override=True)