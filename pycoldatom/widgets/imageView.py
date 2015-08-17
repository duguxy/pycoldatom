import pyqtgraph as pg
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np

from . import imageView_rc
from ..utils.qt import qtstr

class ImageView(QWidget):
	"A simple image viewer"
	foobar = 'hello world'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.image = None



		self.toolbar = QToolBar('setting', self)

		self.autoLevel = True
		self.autoLevelAction = QAction(QIcon(':/icons/autoLevel.png'), 'Auto Level', self)
		self.autoLevelAction.setCheckable(True)
		self.autoLevelAction.setChecked(True)
		self.toolbar.addAction(self.autoLevelAction)

		self.crosshairAction = QAction(QIcon(':/icons/crosshair.png'), 'Cross Hair', self)
		self.crosshairAction.setCheckable(True)
		self.crosshairAction.setChecked(True)
		self.toolbar.addAction(self.crosshairAction)

		self.graphicsLayout = pg.GraphicsLayoutWidget(self)

		self.plot = self.graphicsLayout.addPlot()
		self.plot.setAspectLocked(True)

		self.imageItem = pg.ImageItem()
		self.plot.addItem(self.imageItem)
		self.vLine = pg.InfiniteLine(angle=90, movable=False)
		self.hLine = pg.InfiniteLine(angle=0, movable=False)
		self.plot.addItem(self.vLine, ignoreBounds=True)
		self.plot.addItem(self.hLine, ignoreBounds=True)

		self.histogram = pg.HistogramLUTItem()
		self.histogram.setImageItem(self.imageItem)
		self.graphicsLayout.addItem(self.histogram)

		self.label = pg.LabelItem(justify='left')
		self.graphicsLayout.nextRow()
		self.graphicsLayout.addItem(self.label)

		self.mainLayout = QVBoxLayout()
		self.mainLayout.setContentsMargins(0,0,0,0)
		self.mainLayout.addWidget(self.toolbar)
		self.mainLayout.addWidget(self.graphicsLayout)
		self.setLayout(self.mainLayout)

		self.autoLevelAction.triggered.connect(self.onAutoLevelAction)
		self.crosshairAction.triggered.connect(self.onCrosshairAction)
		self.proxy = pg.SignalProxy(self.imageItem.scene().sigMouseMoved, rateLimit=60,
			slot=self.onMouseMoved)

	def setImage(self, image):
		self.image = image
		self.imageItem.setImage(self.image, autoLevels=False)
		self.histogram.imageChanged(autoLevel=self.autoLevel)

	def getImage(self):
		return self.image

	def getPlot(self):
		return self.plot

	def getImageItem(self):
		return self.imageItem

	def addItem(self, item):
		if item not in self.plot.items:
			self.plot.addItem(item)

	def removeItem(self, item):
		if item in self.plot.items:
			self.plot.removeItem(item)

	def onCrosshairAction(self, checked):
		self.vLine.setVisible(checked)
		self.hLine.setVisible(checked)

	def onAutoLevelAction(self, checked):
		self.autoLevel = checked
		if self.autoLevel:
			self.histogram.imageChanged(autoLevel=True)

	def onMouseMoved(self, pos):
		if self.crosshairAction.isChecked():
			mousePoint = self.plot.vb.mapSceneToView(*pos)
			self.vLine.setPos(mousePoint.x())
			self.hLine.setPos(mousePoint.y())

		if self.image is not None:
			pos = self.imageItem.mapFromScene(*pos)
			x = int(pos.x())
			y = int(pos.y())
			try:
				value = self.image[x,y]
				self.label.setText('x=%d, y=%d, value=%f' % (x, y, value))
			except IndexError:
				pass

	def saveState(self):
		state = {
			'autoLevel': self.autoLevel,
			'gradient': self.histogram.gradient.saveState()
			}
		return state

	def restoreState(self, state):
		self.autoLevelAction.setChecked(state['autoLevel'])
		self.autoLevelAction.triggered.emit()
		self.histogram.gradient.restoreState(state['gradient'])
		# self.autoLevel = state['autoLevel']