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

		self.images = None

		self.init_camera()

	def init_camera(self):
		self.cameraPanel = AndorCamera()
		self.cameraPanel.sigStatusMessage.connect(self.showMessage)
		self.cameraPanel.sigAcquiredData.connect(self.onAcquisition)

	def showMessage(self, msg):
		self.statusBar.showMessage(msg)

	def ctrlWidget(self):
		return self.cameraPanel

	def onAcquisition(self, data):
		self.images = {str(i+1): img for i, img in enumerate(data)}
		# print(self.images)
		self.setOutput(images=self.images)

	def process(self, display=True):
		return {'images': self.images}

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

class AndorGlobalNode(AndorNode):
	nodeName = "Andor Camera Global"
	nodePaths = [('Camera',)]

	def init_camera(self):
		pass

	def init_global(self, flowchart):
		if 'AndorCamera' not in flowchart.addon:
			self.cameraPanel = AndorCamera()
			flowchart.addon['AndorCamera'] = self.cameraPanel
			cameraAction = QAction('camera', self.cameraPanel, triggered=self.cameraPanel.show)
			flowchart.toolbar.addAction(cameraAction)
			flowchart.statusBar.addPermanentWidget(self.cameraPanel.progressBar)
			flowchart.statusBar.addPermanentWidget(self.cameraPanel.tempLabel)
			self.cameraPanel.sigStatusMessage.connect(flowchart.statusBar.showMessage)
		else:
			self.cameraPanel = flowchart.addon['AndorCamera']

		self.cameraPanel.sigAcquiredData.connect(self.onAcquisition)

	def close(self):
		super(AndorNode, self).close()

	def ctrlWidget(self):
		pass

nodelist = [AndorNode, AndorGlobalNode]