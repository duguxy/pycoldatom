from pyqtgraph.flowchart import Node, eq
import pyqtgraph as pg
from PyQt5.QtWidgets import *

class IsocurveNode(Node):
	"""Node for adding isocurve in imageview

	Input terminals:
	- view: imageview object
	- level: the isocurve level
	"""

	nodeName = 'Isocurve'
	nodePaths = [('Display',)]

	def __init__(self, name, **kwargs):
		terminals = {
			'view': {'io': 'in'},
			'level': {'io': 'out'}
		}

		super().__init__(name, terminals=terminals, **kwargs)

		self.view = None

		self.iso = pg.IsocurveItem(level=0.5, pen='g')
		self.iso.setZValue(5)

		self.isoLine = pg.InfiniteLine(angle=0, movable=True, pen='g')
		self.isoLine.setValue(0.5)
		self.isoLine.setZValue(1000)

		self.isoLine.sigDragged.connect(self.updateIsocurve)

		self.panel = QWidget()
		self.panelLayout = QGridLayout(self.panel)

		self.colorButton = pg.ColorButton(self.panel)
		self.panelLayout.addWidget(self.colorButton, 1, 1)

		self.visibleCheckBox = QCheckBox('Visible', self.panel)
		self.visibleCheckBox.setChecked(True)
		self.panelLayout.addWidget(self.visibleCheckBox, 1, 2)

		self.panel.setLayout(self.panelLayout)

		self.visibleCheckBox.toggled.connect(self.setVisible)
		self.colorButton.sigColorChanged.connect(self.setIsoColor)

	def updateIsocurve(self):
		self.iso.setLevel(self.isoLine.value())

	def process(self, view, display=True):
		if view is not None:
			self.view = view
			self.view.addItem(self.iso)
			self.view.addHistItem(self.isoLine)

			self.iso.setData(pg.gaussianFilter(self.view.getImage(), (2, 2)))

			return {'level': self.iso.level}

	def close(self):
		if self.view is not None:
			self.view.removeItem(self.iso)
			self.view.removeHistItem(self.isoLine)
		super().close()

	def setVisible(self, checked):
		self.iso.setVisible(checked)
		self.isoLine.setVisible(checked)

	def setIsoColor(self, colorButton):
		self.iso.setPen(colorButton.color())
		self.isoLine.setPen(colorButton.color())

	def ctrlWidget(self):
		return self.panel

nodelist = [IsocurveNode]