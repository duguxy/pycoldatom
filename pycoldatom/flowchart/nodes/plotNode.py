from pyqtgraph.flowchart import Node
import pyqtgraph as pg
from ...widgets.plot import Plot

class Plot2dNode(Node):
	nodeName = 'Plot2D'
	nodePaths = [('Display',)]
	def __init__(self, name):
		self.plot = Plot()
		super().__init__(name, terminals={}, allowAddInput=True)

	def widget(self):
		return self.plot

	def process(self, display=True, **kwargs):
		if kwargs:
			self.plot.setData(kwargs)

nodelist=[Plot2dNode]