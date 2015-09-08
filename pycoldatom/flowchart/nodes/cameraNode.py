from pyqtgraph.flowchart import Node
from pyclibrary import CParser, CLibrary
import os
import logging
logger = logging.getLogger('flowchart.camera')

import ctypes

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ...widgets.andorCamera import AndorCamera
from ...utils.qt import stateFunc

class AndorNode(Node):
	"""Node controlling Andor iXon Ultra 897 camera

	Output terminals
	- images: acquired images
	"""

	nodeName = "Andor Camera"
	nodePaths = [('Camera',)]

	def __init__(self, name, **kwargs):
		terminals = {
			'images': {'io': 'out'}
		}
		super().__init__(name, terminals=terminals, **kwargs)

		self.images = None

	def init_global(self, flowchart):
		"""The entry point for initialize camera globally"""

		if 'AndorCamera' not in flowchart.addon:
			self.camera = AndorCamera()
			flowchart.addon['AndorCamera'] = self.camera
			flowchart.win.addToolBar(self.camera.toolbar)
			flowchart.statusBar.addPermanentWidget(self.camera.progressBar)
			flowchart.statusBar.addPermanentWidget(self.camera.tempLabel)
			self.camera.sigStatusMessage.connect(flowchart.statusBar.showMessage)
		else:
			self.camera = flowchart.addon['AndorCamera']

		self.camera.sigAcquiredData.connect(self.onAcquisition)
		logger.info('Init camera addon')

	def showMessage(self, msg):
		self.statusBar.showMessage(msg)

	def onAcquisition(self, data):
		self.images = {str(i+1): img for i, img in enumerate(data)}
		self.setOutput(images=self.images)

	def process(self, display=True):
		return {'images': self.images}

	def close(self):
		super().close()

	def saveState(self):
		state = super().saveState()
		state['camera'] = self.camera.saveState()
		return state

	def restoreState(self, state):
		super().restoreState(state)
		self.camera.restoreState(state['camera'])

nodelist = [AndorNode]