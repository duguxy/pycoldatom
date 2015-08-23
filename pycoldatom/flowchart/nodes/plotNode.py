from pyqtgraph.flowchart import Node
from ...widgets.plot import Plot

class Plot2dNode(Node):
	nodeName = 'Plot2D'
	nodePaths = [('Display',)]
	def __init__(self, name):
		self.plot = Plot()
		super().__init__(name, terminals={'data':{'io':'in'}})

	def widget(self):
		return self.plot

	def process(self, data, display=True):
		if data is not None:
			self.plot.setData(data)

nodelist=[Plot2dNode]