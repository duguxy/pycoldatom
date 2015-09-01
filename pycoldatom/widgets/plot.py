import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point
import itertools
from collections import OrderedDict

class Plot(pg.GraphicsLayoutWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot = self.addPlot()
        self.plot.addLegend()
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.addItem(self.plot)
        self.plot.addItem(self.vLine)
        self.plot.addItem(self.hLine)
        self.nextRow()
        self.label = self.addLabel('', col=1, justify='left')
        self.data = None

        self.showCrossHair = False
        self.hLine.setVisible(False)
        self.vLine.setVisible(False)
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
            text = "x=%0.1f " % mousePoint.x()
            for k, v in self.data.items():
                try:
                    text += "%s=%0.1f " % (k, v[index])
                except IndexError:
                    pass
            self.label.setText(text)
            if self.showCrossHair:
                self.vLine.setPos(mousePoint.x())
                self.hLine.setPos(mousePoint.y())

    def setData(self, data, *args, display=True, **kwargs):
        self.data = OrderedDict(sorted([(k,v) for k, v in data.items() if v is not None]))
        self.plot.clear()
        self.plot.legend.removeAllItem()
        Colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
        for (k,v), c in zip(self.data.items(), itertools.cycle(Colors)):
            self.plot.plot(v, pen=c, name=k)

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

