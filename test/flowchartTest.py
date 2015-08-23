from init_test import *

from PyQt5.QtWidgets import QApplication

class FlowchartTest(unittest.TestCase):
	def setUp(self):
		from pycoldatom.flowchart import Flowchart
		self.app = QApplication([])
		self.fc = Flowchart()
		self.fcwidget = self.fc.widget()

	def test_reload(self):
		self.fcwidget.chartWidget.reloadLibrary()

	def test_imageView(self):
		lena = self.fc.createNode('Lena')
		imv = self.fc.createNode('ImageView')
		roi = self.fc.createNode('RectRoi')
		self.fc.connectTerminals(lena['lena'], imv['image'])
		self.fc.connectTerminals(imv['view'], roi['view'])
		lena.update()
		self.fc.process()

	def test_camera(self):
		cam = self.fc.createNode('Andor Camera')

	def test_file(self):
		lm = self.fc.createNode('Load mat')
		sm = self.fc.createNode('Save mat')
		ds = self.fc.createNode('Dict Select')
		dc = self.fc.createNode('Dict Combine')

	def test_func(self):
		for node in ['exp', 'log', 'add', 'subtract', 'true_divide', 'multiply']:
			self.fc.createNode(node)

	def test_fit(self):
		fitg = self.fc.createNode('FitGaussian')

	def tearDown(self):
		pass

if __name__ == '__main__':
	unittest.main()