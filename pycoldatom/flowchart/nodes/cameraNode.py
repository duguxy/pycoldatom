from pyqtgraph.flowchart import Node
from pyclibrary import CParser, CLibrary
import os
import ctypes

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ...widgets.andorCamera import AndorCamera
from ...utils.qt import stateFunc

class AndorNode(Node):
	nodeName = "Andor Camera"
	nodePaths = [('Camera',)]

	def __init__(self, name, **kwargs):
		terminals = {
			'images': {'io': 'out'}
		}
		super().__init__(name, terminals=terminals, **kwargs)

		self.cameraPanel = AndorCamera()
		self.cameraPanel.sigStatusMessage.connect(self.showMessage)
		self.cameraPanel.sigAcquiredData.connect(self.onAcquisition)

	def showMessage(self, msg):
		self.statusBar.showMessage(msg)

	def ctrlWidget(self):
		return self.cameraPanel

	def onAcquisition(self, data):
		self.setOutput(images={str(i): img for i, img in enumerate(data)})

	def close(self):
		self.cameraPanel.close()
		super().close()

	def saveState(self):
		state = super().saveState()
		state['camera'] = self.cameraPanel.saveState()
		return state

	def restoreState(self, state):
		super().restoreState(state)
		self.cameraPanel.restoreState(state['camera'])

nodelist = [AndorNode]