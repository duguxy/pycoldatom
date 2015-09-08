from pyqtgraph.flowchart import Node
from pyqtgraph.parametertree import Parameter, ParameterTree

from ...widgets.fileBrowser import FileBrowser

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os

from scipy.io import loadmat, savemat

from ...utils.autosave import getAutosaveFileName
from ...utils.cicerolistener import CiceroListener

class LoadmatNode(Node):
	"""Node for loading a .mat file of MATLAB.
	Files are selected in a simple explorer

	Output terminals:
	- title: file name
	- data: return of scipy.loadmat
	"""

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
	"""Node for saving mat file and automatically generate filename
	This node is used only with Cicero modified to support zmq.

	Input terminals:
	- data: data to be saved in mat. Usually a dict

	Output terminals:
	- title: saved file name
	"""

	nodeName = 'Save mat'
	nodePaths = [('File',)]

	def __init__(self, name):
		super().__init__(name, terminals={'data':{'io':'in'}, 'title': {'io': 'out'}}, allowAddInput=True)

		self.title = None

		self.panel = QWidget()
		self.layout = QGridLayout(self.panel)

		self.pathLabel = QLabel('Path')
		self.layout.addWidget(self.pathLabel, 0, 0)
		self.pathEdit = QLineEdit()
		self.layout.addWidget(self.pathEdit, 0, 1)
		self.selectFolderButton = QPushButton('...')
		self.selectFolderButton.setMaximumWidth(30)
		self.selectFolderButton.clicked.connect(self.onSelectFolder)
		# self.selectFolderButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
		self.layout.addWidget(self.selectFolderButton, 0, 2)

		self.folderSuffixLabel = QLabel('Folder Suffix', self.panel)
		self.layout.addWidget(self.folderSuffixLabel, 1, 0)
		self.folderSuffixEdit = QLineEdit('')
		self.layout.addWidget(self.folderSuffixEdit, 1, 1, 1, 2)

		self.fileInfixLabel = QLabel('File infix')
		self.layout.addWidget(self.fileInfixLabel, 2, 0)
		self.fileInfixEdit = QLineEdit('')
		self.layout.addWidget(self.fileInfixEdit, 2, 1, 1, 2)

		# self.fileSuffixLabel = QLabel('File suffix')
		# self.layout.addWidget(self.fileSuffixLabel, 3, 0)
		# self.fileSuffixEdit = QLineEdit('')
		# self.layout.addWidget(self.fileSuffixEdit, 3, 1, 1, 2)

		self.panel.setLayout(self.layout)
		self.listener = CiceroListener()
		self.listener.keep_running = True
		self.listener.start()

	def onSelectFolder(self):
		path = QFileDialog.getExistingDirectory(self.panel)
		self.pathEdit.setText(path)

	def process(self, data, display=True):
		if data is not None:
			time = self.listener.commands['time']
			suffix = ''
			if 'listvalue' in self.listener.commands:
				listvalue = self.listener.commands['listvalue']
				for variable, value in zip(listvalue[0::2], listvalue[1::2]):
					suffix += '%s=%s' % (variable, value)
			filename = getAutosaveFileName(time, suffix, self.fileInfixEdit.text(), self.folderSuffixEdit.text())
			self.title = filename
			path = os.path.join(self.pathEdit.text(), filename)
			if os.path.exists(path):
				return

			dirs = os.path.dirname(path)
			if not os.path.isdir(dirs):
				os.makedirs(dirs)
			savemat(path, data)
		return {'title': self.title}

	def ctrlWidget(self):
		return self.panel

	def close(self):
		self.listener.keep_running = False
		super().close()

	def saveState(self):
		state = super().saveState()
		state['savepath'] = self.pathEdit.text()
		state['foldersuffix'] = self.folderSuffixEdit.text()
		state['fileinfix'] = self.fileInfixEdit.text()
		# state['filesuffix'] = self.fileSuffixEdit.text()
		return state

	def restoreState(self, state):
		super().restoreState(state)
		self.pathEdit.setText(state['savepath'])
		self.folderSuffixEdit.setText(state['foldersuffix'])
		self.fileInfixEdit.setText(state['fileinfix'])
		# self.fileSuffixEdit.setText(state['filesuffix'])

nodelist = [LoadmatNode, SavematNode]