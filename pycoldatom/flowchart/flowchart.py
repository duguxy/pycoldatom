import pyqtgraph.flowchart as pgfc
from pyqtgraph.widgets.FileDialog import FileDialog
from .nodeLibrary import NodeLibrary
from pyqtgraph import configfile 

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from . import flowchart_rc

class Flowchart(pgfc.Flowchart):

	def __init__(self, **kwargs):
		nodeLibrary = NodeLibrary()
		super().__init__(library=nodeLibrary, **kwargs)

		self.win = QMainWindow()
		self.splitter = QSplitter()
		self.splitter.addWidget(self.widget())
		self.mdiArea = QMdiArea(self.win)
		self.splitter.addWidget(self.mdiArea)
		self.win.setCentralWidget(self.splitter)

		self.toolbar = self.win.addToolBar('Flowchart')
		self.runAction = QAction(QIcon(':start.png'), 'Start', self.win, triggered=self.process)
		self.toolbar.addAction(self.runAction)

		self.refreshAction = QAction(QIcon(':refresh.png'), 'Refresh', self.win, triggered=self.updateCurrentNode)
		self.toolbar.addAction(self.refreshAction)

		self.statusBar = QStatusBar(self.win)
		self.win.setStatusBar(self.statusBar)

		app = QCoreApplication.instance()
		app.lastWindowClosed.connect(self.clear)

	def updateCurrentNode(self):
		name = self.mdiArea.currentSubWindow().windowTitle()
		self._nodes[name].update()

	def createNode(self, *args, **kwargs):
		node = super().createNode(*args, **kwargs)

		if hasattr(node, 'widget'):
			widget = node.widget()
			flags = Qt.CustomizeWindowHint | \
				Qt.WindowTitleHint | \
				Qt.WindowMinimizeButtonHint | \
				Qt.WindowMaximizeButtonHint
			subwin = self.mdiArea.addSubWindow(widget, flags=flags)
			subwin.resize(600, 600)
			def setWindowTitle(node, oldname):
				widget.setWindowTitle(node.name())
			node.setWindowTitle = setWindowTitle
			node.setWindowTitle(node, None)
			node.sigRenamed.connect(node.setWindowTitle)
			widget.show()

		node.flowchart = self
		node.statusBar = self.statusBar

		return node