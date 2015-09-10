from pyqtgraph.flowchart import Node
from pyqtgraph.console import ConsoleWidget

from scipy.misc import lena

from PyQt5.QtWidgets import *

class ConsoleNode(Node):
	"""Node providing a console for showing results and debugging

	Input terminals:
	- title: the title of current results. Title won't be printed until it is changed
	- added inputs: item to be print in the console
	"""

	nodeName = 'Console'
	nodePaths = [('Debug',)]

	def __init__(self, name):
		super().__init__(name, terminals={'title':{'io':'in'}}, allowAddInput=True)
		self.console = ConsoleWidget()
		self.title = None

	def process(self, title, display=True, **kwargs):
		if title is not None:
			if self.title != title:
				self.console.write('<b>%s</b><br>' % title, html=True)
				self.title = title
		for k, v in sorted(kwargs.items()):
			if v is None:
				continue
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
	"""Node for outputing a standard Lena image

	Output terminals:
	- lena: lena image
	"""

	nodeName = 'Lena'
	nodePaths = [('Debug',)]
	def __init__(self, name, **kwargs):
		terminals={
			'lena': {'io':'out'} # lena image
		}
		super().__init__(name, terminals=terminals, **kwargs)

	def process(self, display=True):
		return {'lena': lena()}

class EvalNode(Node):
	"""Node for eval

	Output terminals:
	- output: return of eval
	"""

	nodeName = 'Eval'
	nodePaths = [('Debug',)]

	def __init__(self, name, **kwargs):
		terminals={
			'output': {'io':'out'} # result of eval
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

nodelist = [LenaNode, ConsoleNode, EvalNode]