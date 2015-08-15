from pyqtgraph.flowchart import Node

from scipy.misc import lena

class LenaNode(Node):
	nodeName = 'Lena'
	nodePaths = [('Debug',)]
	def __init__(self, name, **kwargs):
		terminals={
			'lena': {'io':'out'}
		}
		super().__init__(name, terminals=terminals, **kwargs)

	def process(self, display=True):
		return {'lena': lena()}

nodelist = [LenaNode]