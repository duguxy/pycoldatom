from pyqtgraph.flowchart import Node
import pyqtgraph as pg
import numpy as np
import pickle
import os

from PyQt5.QtWidgets import *

class RoiNode(Node):
	"""Node for adding region-of-interest in imageview

	Input terminals:
	- view: imageview object

	Output terminals:
	- pos: ROI position
	- image: image in the ROI
	- mask: the mask array, false inside the ROI, true outside 
	- maskedImage: maksedarray object of numpy, with images outside the ROI masked
	"""

	roiDirectoryPath = ''

	def __init__(self, name, **kwargs):
		terminals = {
			'view': {'io': 'in'},
			'pos': {'io': 'out'},
			'image': {'io': 'out'},
			'mask': {'io': 'out'},
			'maskedImage': {'io': 'out'}
		}
		super().__init__(name, terminals=terminals, **kwargs)
		self.roi = self.makeRoi()
		self.panel = QWidget()
		self.panelLayout = QGridLayout(self.panel)

		self.colorButton = pg.ColorButton(self.panel)
		self.panelLayout.addWidget(self.colorButton, 1, 1)

		self.visibleCheckBox = QCheckBox('Visible', self.panel)
		self.visibleCheckBox.setChecked(True)
		self.panelLayout.addWidget(self.visibleCheckBox, 1, 2)

		self.saveButton = QPushButton('Save', self.panel)
		self.panelLayout.addWidget(self.saveButton, 2, 1)

		self.loadButton = QPushButton('Load', self.panel)
		self.panelLayout.addWidget(self.loadButton, 2, 2)

		self.panel.setLayout(self.panelLayout)

		self.colorButton.sigColorChanged.connect(self.setRoiColor)
		self.visibleCheckBox.toggled.connect(self.setVisible)
		self.saveButton.clicked.connect(self.saveRoi)
		self.loadButton.clicked.connect(self.loadRoi)

		self.view = None

	def saveRoi(self):
		path = QFileDialog.getSaveFileName(self.panel, "Save ROI", self.roiDirectoryPath, "Regin of Interset (*.roi)", )[0]
		if path:
			# if not path.endswith('.roi'):
			# 	path += '.roi'
			self.roiDirectoryPath = os.path.dirname(path)
			with open(path, 'wb') as f:
				pickle.dump(self.roi.saveState(), f)

	def loadRoi(self):
		path = QFileDialog.getOpenFileName(self.panel, "Open ROI", self.roiDirectoryPath, "Regin of Interset (*.roi)", )[0]
		if path:
			self.roiDirectoryPath = os.path.dirname(path)
			with open(path, 'rb') as f:
				self.roi.setState(pickle.load(f))

	def setVisible(self, checked):
		self.roi.setVisible(checked)

	def setRoiColor(self, colorButton):
		self.roi.setPen(colorButton.color())

	def makeRoi(self):
		raise NotImplemented

	def getMask(self, data, img):
		raise NotImplemented

	def process(self, view, display=True):
		if view is not None:
			view.addItem(self.roi)
			self.view = view
			image = view.getImage()
			imageItem = view.getImageItem()
			result = {}
			result['image'] = self.roi.getArrayRegion(image, imageItem)
			result['mask'] = self.getMask(image, imageItem)
			result['pos'] = self.roi.pos()
			result['maskedImage'] = np.ma.array(image, mask=result['mask'])
			return result

	# def setInput(self, **args):
	# 	"""Set the values on input terminals. For most nodes, this will happen automatically through Terminal.inputChanged.
	# 	This is normally only used for nodes with no connected inputs."""
	# 	changed = True
	# 	for k, v in args.items():
	# 		term = self._inputs[k]
	# 		# oldVal = term.value()
	# 		# if not eq(oldVal, v):
	# 		# 	changed = True
	# 		term.setValue(v, process=False)
	# 	if changed and '_updatesHandled_' not in args:
	# 		self.update()

	def close(self):
		if self.view is not None:
			self.view.removeItem(self.roi)
		super().close()

	def ctrlWidget(self):
		return self.panel

	def saveState(self):
		state = super().saveState()
		state['roi'] = self.roi.saveState()
		state['color'] = self.colorButton.saveState()
		state['path'] = self.roiDirectoryPath
		return state

	def restoreState(self, state):
		super().restoreState(state)
		self.roi.setState(state['roi'])
		self.colorButton.restoreState(state['color'])
		self.roiDirectoryPath = state['path']

class RectRoiNode(RoiNode):
	"""Rectangle ROI node"""

	nodeName = 'RectRoi'
	nodePaths = [('Display',)]
	def makeRoi(self):
		roi = pg.RectROI([20, 20], [100, 100])
		roi.addScaleHandle([0, 0], [1, 1])
		roi.addScaleHandle([0, 1], [1, 0])
		roi.addScaleHandle([1, 0], [0, 1])
		return roi

	def getMask(self, data, img):
		sl, tr = self.roi.getArraySlice(data, img)
		mask = np.ones(data.shape)
		mask[sl] = 0
		return mask

nodelist = [RectRoiNode]