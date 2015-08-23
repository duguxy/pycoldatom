# import sys
# sys.path.insert(0, "D:/src/pyqtgraph/")
# import pyqtgraph
# print(pyqtgraph.__file__)

from init_flowchart import *

app = QApplication([])
fc = Flowchart()

fc.win.show()
app.exec_()