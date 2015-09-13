from pyqtgraph.flowchart import Node
import pyqtgraph as pg
from ...widgets.plot import Plot

class Plot2dNode(Node):
	"""Node for plotting 2 dimensional data points

	Input terminals:
	- added inputs: data to be plotted
	"""

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

	def saveState(self):
		state = super().saveState()
		state['geometry'] = self.subwin.geometry()
		return state

	def restoreState(self, state):
		super().restoreState(state)
		self.subwin.setGeometry(state['geometry'])

nodelist=[Plot2dNode]