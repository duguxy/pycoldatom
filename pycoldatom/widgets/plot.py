import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point

class Plot(pg.GraphicsLayoutWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot = self.addPlot()
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.label = pg.LabelItem(justify='left')
        self.addItem(self.plot)
        self.plot.addItem(self.vLine)
        self.plot.addItem(self.hLine)
        self.nextRow()
        self.addItem(self.label)
        self.data = None

        self.showCrossHair = True
        self.crossHairAction = QtGui.QAction("Cross Hair", self, checkable=True)
        self.crossHairAction.triggered.connect(self.onCrossHair)
        self.crossHairAction.setChecked(self.showCrossHair)
        self.plot.vb.menu.addAction(self.crossHairAction)

        self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.data is not None and self.plot.sceneBoundingRect().contains(pos):
            mousePoint = self.plot.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            if index > 0 and index < len(self.data):
                self.label.setText("x=%0.1f, y=%0.1f" % (mousePoint.x(), self.data[index]))
                if self.showCrossHair:
                    self.vLine.setPos(mousePoint.x())
                    self.hLine.setPos(self.data[index])

    def setData(self, data, *args, **kwargs):
        self.data = data
        self.plot.clearPlots()
        self.plot.plot(data, *args, **kwargs)

    def onCrossHair(self, checked):
        self.showCrossHair = checked
        self.vLine.setVisible(checked)
        self.hLine.setVisible(checked)

    def saveState(self):
        state = {}
        state['showCrossHair'] = self.showCrossHair
        return state

    def restoreState(self, state):
        self.showCrossHair = state['showCrossHair']