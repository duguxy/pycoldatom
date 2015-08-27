import sys

from PyQt5.QtWidgets import QApplication
from .flowchart import Flowchart

app = QApplication([])
fc = Flowchart()
fc.win.show()
app.exec_()