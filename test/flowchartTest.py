import os, sys

if __name__ == "__main__" and (__package__ is None or __package__==''):
	parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	sys.path.insert(0, parent_dir)

import unittest
from PyQt5.QtWidgets import QApplication

class TestStringMethods(unittest.TestCase):
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
		self.fc.process()

	def tearDown(self):
		pass

if __name__ == '__main__':
	unittest.main()