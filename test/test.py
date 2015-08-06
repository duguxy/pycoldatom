import os, sys

if __name__ == "__main__" and (__package__ is None or __package__==''):
	parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	sys.path.insert(0, parent_dir)

import unittest
from PyQt5.QtWidgets import QApplication

from pycoldatom.flowchart import Flowchart
app = QApplication([])
fc = Flowchart()

imv = fc.createNode('ImageView')
imv2 = fc.createNode('ImageView')
lena = fc.createNode('Lena')
roi = fc.createNode('RectRoi')
fc.connectTerminals(lena['lena'], imv['image'])
fc.connectTerminals(imv['view'], roi['view'])
fc.connectTerminals(roi['image'], imv2['image'])
lena.setInput(dummy=True)
# fc.process()
fc.win.show()
app.exec_()