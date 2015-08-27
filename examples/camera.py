from init_flowchart import *

app = QApplication([])
fc = Flowchart()

cam = fc.createNode('Andor Camera Global')
# cam.cameraPanel.onConnect()
fc.win.show()
app.exec_()