from init_flowchart import *

app = QApplication([])
fc = Flowchart()

lena = fc.createNode('Lena', pos=(0, 100))
imv = fc.createNode('ImageView', pos=(200, 100))
roi = fc.createNode('RectRoi', pos=(400, 100))
imv2 = fc.createNode('ImageView', pos=(600, 100))
fc.connectTerminals(lena['lena'], imv['image'])
fc.connectTerminals(imv['view'], roi['view'])
fc.connectTerminals(roi['image'], imv2['image'])
lena.update()
fc.win.show()
app.exec_()