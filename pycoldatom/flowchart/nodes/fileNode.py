from pyqtgraph.flowchart import Node

from ...widgets.fileBrowser import FileBrowser

from PyQt5.QtWidgets import QListView
from PyQt5.QtGui import QStandardItemModel, QStandardItem

import os

from scipy.io import loadmat

class LoadmatNode(Node):
	nodeName = 'Load mat'
	nodePaths = [('File',)]

	def __init__(self, name):
		super().__init__(name, terminals={'data':{'io':'out'}})
		self.fileBrowser = FileBrowser()
		self.matdata = None
		self.fileBrowser.clicked.connect(self.onFileSelected)

	def onFileSelected(self, index):
		path = self.fileBrowser.filemodel.filePath(index)
		self.dir, basefilename = os.path.split(path)
		filename, fileext = os.path.splitext(basefilename)
		if fileext.lower() == '.mat':
			self.matdata = loadmat(path)
			self.setOutput(data=self.matdata)

	def process(self, display=True):
		return {'data':self.matdata}

	def widget(self):
		return self.fileBrowser()

class SavematNode(Node):
	nodeName = 'Save mat'
	nodePaths = [('File',)]

	def __init__(self, name):
		super().__init__(name, terminals={'title':{'io':'in'}}, allowAddInput=True)

	def process(self, title, display=True):
		pass

class DictSelectNode(Node):
	nodeName = 'Dict Select'
	nodePaths = [('Misc',)]

	def __init__(self, name):
		super().__init__(name, terminals={'data':{'io':'in'}, 'selected': {'io': 'out'}}, allowAddOutput=True)

		self.labelview = QListView()
		self.labelmodel = QStandardItemModel()
		self.labelview.setModel(self.labelmodel)
		self.labelview.clicked.connect(self.onLabelSelected)

		self.data = None
		self.label = None

	def ctrlWidget(self):
		return self.labelview

	def onLabelSelected(self, index):
		self.label = index.data()
		self.setOutput(value=self.data[self.label])

	def setLabels(self, data):
		self.data = data
		self.labelmodel.clear()
		for label in self.data:
			if not label.startswith('_'):
				self.labelmodel.appendRow(QStandardItem(label))
		if self.label is not None and self.label in self.data:
			item = self.labelmodel.findItems(self.label)[0]
			index = self.labelmodel.indexFromItem(item)
			self.labelview.setCurrentIndex(index)
			self.onLabelSelected(index)

	def process(self, data, display=True):
		self.setLabels(data)
		result = {}
		
		for k in self.outputs().keys():
			if k == 'selected' and self.label in self.data:
				result[k] = self.data[self.label]
			elif k in self.data:
				result[k] = self.data[k]

		return result

nodelist = [LoadmatNode, DictSelectNode]