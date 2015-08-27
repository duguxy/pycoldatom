from init_flowchart import *

app = QApplication([])
fc = Flowchart()

cam = fc.createNode('Andor Camera')
# cam.cameraPanel.onConnect()
fc.win.show()
app.exec_()