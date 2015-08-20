from pyqtgraph.flowchart import Node
import pyqtgraph as pg
import numpy as np

class RoiNode(Node):
	def __init__(self, name, **kwargs):
		terminals = {
			'view': {'io': 'in'},
			'pos': {'io': 'out'},
			'image': {'io': 'out'},
			'mask': {'io': 'out'}
		}
		super().__init__(name, terminals=terminals, **kwargs)
		self.roi = self.makeRoi()
		self.colorButton = pg.ColorButton()
		self.view = None

	def makeRoi(self):
		raise NotImplemented

	def getMask(self, data, img):
		raise NotImplemented

	def process(self, view, display=True):
		if view is not None:
			view.addItem(self.roi)
			self.view = view
			result = {}
			result['image'] = self.roi.getArrayRegion(view.getImage(), view.getImageItem())
			result['mask'] = self.getMask(view.getImage(), view.getImageItem())
			result['pos'] = self.roi.pos()
			return result

	def close(self):
		if self.view is not None:
			self.view.removeItem(self.roi)
		super().close()

	def ctrlWidget(self):
		return self.colorButton

	def saveState(self):
		state = super().saveState()
		state['roi'] = self.roi.saveState()
		return state

	def restoreState(self, state):
		super().restoreState(state)
		self.roi.setState(state['roi'])

class RectRoiNode(RoiNode):
	nodeName = 'RectRoi'
	nodePaths = [('ROI',)]
	def makeRoi(self):
		roi = pg.RectROI([20, 20], [100, 100])
		roi.addScaleHandle([0, 0], [1, 1])
		roi.addScaleHandle([0, 1], [1, 0])
		roi.addScaleHandle([1, 0], [0, 1])
		return roi

	def getMask(self, data, img):
		sl, tr = self.roi.getArraySlice(data, img)
		mask = np.zeros(data.shape)
		mask[sl] = 1.0
		return mask

nodelist = [RectRoiNode]