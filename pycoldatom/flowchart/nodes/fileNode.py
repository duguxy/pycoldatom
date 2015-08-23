from pyqtgraph.flowchart import Node

from ...widgets.fileBrowser import FileBrowser

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os

from scipy.io import loadmat

class LoadmatNode(Node):
	nodeName = 'Load mat'
	nodePaths = [('File',)]

	def __init__(self, name):
		super().__init__(name, terminals={'data':{'io':'out'}, 'title': {'io': 'out'}})
		self.fileBrowser = FileBrowser()
		self.matdata = None
		self.filename = None
		self.fileBrowser.clicked.connect(self.onFileSelected)

	def onFileSelected(self, index):
		path = self.fileBrowser.filemodel.filePath(index)
		self.dir, basefilename = os.path.split(path)
		filename, fileext = os.path.splitext(basefilename)
		if fileext.lower() == '.mat':
			self.matdata = loadmat(path)
			self.filename = filename
			self.setOutput(data=self.matdata, title=self.filename)

	def process(self, display=True):
		return {'data':self.matdata, 'title':self.filename}

	def widget(self):
		return self.fileBrowser

	def saveState(self):
		state = super().saveState()
		state['geometry'] = self.subwin.geometry()
		return state

	def restoreState(self, state):
		super().restoreState(state)
		self.subwin.setGeometry(state['geometry'])

class SavematNode(Node):
	nodeName = 'Save mat'
	nodePaths = [('File',)]

	def __init__(self, name):
		super().__init__(name, terminals={'title':{'io':'in'}}, allowAddInput=True)

		self.panel = QWidget()
		self.layout = QVBoxLayout(self.panel)
		self.pathLayout = QHBoxLayout()
		self.pathLabel = QLabel('Path')
		self.pathLayout.addWidget(self.pathLabel)
		self.pathEdit = QLineEdit()
		self.pathLayout.addWidget(self.pathEdit)
		self.selectFolderButton = QPushButton('...')
		self.selectFolderButton.setMaximumWidth(30)
		self.selectFolderButton.clicked.connect(self.onSelectFolder)
		# self.selectFolderButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
		self.pathLayout.addWidget(self.selectFolderButton)
		self.layout.addLayout(self.pathLayout)
		self.panel.setLayout(self.layout)

	def onSelectFolder(self):
		path = QFileDialog.getExistingDirectory(self.panel)
		self.pathEdit.setText(path)

	def process(self, title, display=True):
		pass

	def ctrlWidget(self):
		return self.panel

	def saveState(self):
		state = super().saveState()
		state['savepath'] = self.pathEdit.text()
		return state

	def restoreState(self, state):
		super().restoreState(state)
		self.pathEdit.setText(state['savepath'])

nodelist = [LoadmatNode, SavematNode]