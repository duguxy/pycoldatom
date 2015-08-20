from pyqtgraph.flowchart import Node
from pyqtgraph.console import ConsoleWidget

from scipy.misc import lena

from PyQt5.QtWidgets import *

class ConsoleNode(Node):
	nodeName = 'Console'
	nodePaths = [('Debug',)]

	def __init__(self, name):
		super().__init__(name, terminals={'title':{'io':'in'}}, allowAddInput=True)
		self.console = ConsoleWidget()

	def process(self, title, display=True, **kwargs):
		if title is not None:
			self.console.write('<b>%s</b><br>' % title, html=True)
		for k, v in kwargs.items():
			self.console.locals()[k+'_'] = v
			self.console.write('%s: %s\n' % (k, v))
		self.console.write('\n')

	def widget(self):
		return self.console

	def saveState(self):
		state = super().saveState()
		state['geometry'] = self.subwin.geometry()
		return state

	def restoreState(self, state):
		super().restoreState(state)
		self.subwin.setGeometry(state['geometry'])

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

class DebugOutputNode(Node):
	nodeName = 'Output'
	nodePaths = [('Debug',)]
	def __init__(self, name, **kwargs):
		terminals={
			'output': {'io':'out'}
		}
		super().__init__(name, terminals=terminals, **kwargs)

	def setOutput(output):
		self.out = output
		self.setOutput(output=self.out)

	def process(self, display=True):
		return {'output': self.out}

class EvalNode(Node):
	nodeName = 'Eval'
	nodePaths = [('Debug',)]

	def __init__(self, name, **kwargs):
		terminals={
			'output': {'io':'out'}
		}
		super().__init__(name, terminals=terminals, allowAddInput=True, **kwargs)

		self.evalEdit = QLineEdit()

	def setOutput(output):
		self.out = output
		self.setOutput(output=self.out)

	def process(self, display=True, **kwargs):
		return {'output': eval(self.evalEdit.text(), kwargs)}

	def ctrlWidget(self):
		return self.evalEdit

	def saveState(self):
		state = super().saveState()
		state['eval'] = self.evalEdit.text()
		return state

	def restoreState(self, state):
		super().restoreState(state)
		self.evalEdit.setText(state['eval'])

nodelist = [LenaNode, DebugOutputNode, ConsoleNode, EvalNode]