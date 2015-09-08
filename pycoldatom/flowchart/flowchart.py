#!/usr/bin/env python
# flowchart.py

import pyqtgraph.flowchart as pgfc
from pyqtgraph.widgets.FileDialog import FileDialog
from .nodeLibrary import NodeLibrary
from pyqtgraph import configfile 

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from . import flowchart_rc
from ..utils.qt import qtstr
from ..widgets.logger import LoggerDialog

class Flowchart(pgfc.Flowchart):
	"""Flowchart with MDI windows for nodes"""

	def __init__(self, **kwargs):
		self.loggerDialog = LoggerDialog()

		nodeLibrary = NodeLibrary()
		super().__init__(library=nodeLibrary, **kwargs)

		self.win = QMainWindow() # main window of flowchart
		self.win.setWindowTitle('Cold Atom Flowchart')
		self.splitter = QSplitter()
		self.splitter.addWidget(self.widget())
		self.mdiArea = QMdiArea(self.win)
		self.splitter.addWidget(self.mdiArea)
		self.win.setCentralWidget(self.splitter)

		self.toolbar = self.win.addToolBar('Flowchart')

		self.refreshAction = QAction(QIcon(':refresh.png'), 'Refresh', self.win, triggered=self.updateCurrentNode)
		self.toolbar.addAction(self.refreshAction)
		self.loggerAction = QAction('Log', self.win, triggered=self.loggerDialog.showFront)
		self.toolbar.addAction(self.loggerAction)

		self.statusBar = QStatusBar(self.win)
		self.win.setStatusBar(self.statusBar)

		app = QCoreApplication.instance()
		app.lastWindowClosed.connect(self.clear)
		app.lastWindowClosed.connect(self.clear_addon)

		self.addon = {}

	def updateCurrentNode(self):
		"""Update the node whose subwindow has focus"""

		name = self.mdiArea.currentSubWindow().windowTitle()
		self._nodes[name].update()

	def createNode(self, *args, **kwargs):
		"""Overrided method for registering sub windows of nodes and global addons"""

		node = super().createNode(*args, **kwargs)

		if hasattr(node, 'widget'):
			widget = node.widget()
			flags = Qt.CustomizeWindowHint | \
				Qt.WindowTitleHint | \
				Qt.WindowMinimizeButtonHint | \
				Qt.WindowMaximizeButtonHint
			node.subwin = self.mdiArea.addSubWindow(widget, flags=flags)
			node.subwin.resize(widget.size())
			self.setSubWindowTitle(node, None)
			node.sigRenamed.connect(self.setSubWindowTitle)
			node.sigClosed.connect(self.removeSubWindow)
			widget.show()

		node.flowchart = self
		node.statusBar = self.statusBar

		# if a node supports a global addon, it will initiate here
		if hasattr(node, 'init_global'):
			node.init_global(self)

		return node

	def setSubWindowTitle(self, node, oldname):
		node.widget().setWindowTitle(node.name())

	def removeSubWindow(self, node):
		self.mdiArea.removeSubWindow(node.subwin)

	def saveState(self):
		state = super().saveState()
		state['geometry'] = self.win.geometry()
		return state

	def restoreState(self, state, **kwargs):
		self.win.setGeometry(state['geometry'])
		state = super().restoreState(state, **kwargs)

	def clear_addon(self):
		"""Close all global addons"""

		for k, a in self.addon.items():
			a.close()