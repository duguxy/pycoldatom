from pyqtgraph.flowchart import Node
from ...widgets.imageView import ImageView

class ImageViewNode(Node):
	""" Node for viewing images

	Input terminals:
	- image: image to be shown

	Output terminals:
	- view: the ImageView object
	"""

	nodeName = 'ImageView'
	nodePaths = [('Display',)]

	def __init__(self, name, **kwargs):
		terminals = {
			'image': {'io': 'in'},
			'view': {'io': 'out'}
		}
		super().__init__(name, terminals=terminals, **kwargs)
		self.imageView = ImageView()
		self.imageView.resize(600, 600)

	def process(self, image, display=True):
		self.imageView.setImage(image)
		return {'view': self.imageView}

	def widget(self):
		return self.imageView

	def saveState(self):
		state = super().saveState()
		state['imageview'] = self.imageView.saveState()
		state['geometry'] = self.subwin.geometry()
		return state

	def restoreState(self, state):
		super().restoreState(state)
		self.imageView.restoreState(state['imageview'])
		self.subwin.setGeometry(state['geometry'])

nodelist = [ImageViewNode]