from pyqtgraph.flowchart import Node
import numpy as np
from ...functions.fringe import FringeRemove

from pyqtgraph.parametertree import Parameter, ParameterTree

class FringeRemoveNode(Node):
	"""Node for removing fringes"""

	nodeName = 'FringeRemove'
	nodePaths = [('Analysis',)]

	def __init__(self, name):
		terminals = {
			'sig':{'io':'in'},
			'ref':{'io':'in'},
			'bkg':{'io':'in'},
			'sigMask': {'io':'in'},
			'ref1':{'io':'out', 'bypass': 'ref'}
		}
		super().__init__(name, terminals=terminals)

		paras_property = [
			{'name': 'rank', 'type': 'int', 'readonly': True},
			{'name': 'rankLimit', 'type': 'int', 'value': 100},
			{'name': 'trunc', 'type': 'float'},
			{'name': 'updateLib', 'type': 'bool'},
			{'name': 'reset', 'type': 'action'}
		]

		self.paras = Parameter.create(name='params', type='group', children=paras_property)
		self.paratree = ParameterTree()
		self.paratree.setParameters(self.paras, showTop=False)
		self.remover = FringeRemove()

		self.paras.param('reset').sigActivated.connect(self.remover.reset)
	
	def onReset(self):
		self.remover.reset()
		self.paras['rank'] = 0

	def ctrlWidget(self):
		return self.paratree

	def process(self, sig, ref, bkg, sigMask, display=True):
		self.remover.setTrunc(self.paras['trunc'])
		ref = ref - bkg
		if self.paras['updateLib'] and self.paras['rank'] <= self.paras['rankLimit']:
			self.remover.updateLibrary(ref)
			self.paras['rank'] = self.remover.rank
		sig = sig - bkg
		coef, ref = self.remover.reconstruct(np.ma.array(sig, mask=sigMask))
		ref = ref.reshape(512, 512) + bkg
		return {'ref1': ref}

	def saveState(self):
		state = super().saveState()
		state['paras'] = self.paras.saveState()
		return state

	def restoreState(self, state):
		super().restoreState(state)
		self.paras.restoreState(state['paras'])

nodelist = [FringeRemoveNode]