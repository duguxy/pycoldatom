from pyqtgraph.flowchart import Node
from ...widgets.imageView import ImageView

class ImageViewNode(Node):
	nodeName = 'ImageView'
	nodePaths = [('Display',)]

	def __init__(self, name, **kwargs):
		terminals = {
			'image': {'io': 'in'},
			'view': {'io': 'out'}
		}
		super().__init__(name, terminals=terminals, **kwargs)
		self.imageView = ImageView()

	def process(self, image, display=True):
		self.imageView.setImage(image)
		return {'view': self.imageView}

	def widget(self):
		return self.imageView

nodelist = [ImageViewNode]