from init_flowchart import *

app = QApplication([])
fc = Flowchart()

lm = fc.createNode('Load mat', pos=(0, 100))
ds = fc.createNode('Dict Select', pos=(200, 100))
imv = fc.createNode('ImageView', pos=(400, 100))
sm = fc.createNode('Save mat', pos=(600, 100))
roi = fc.createNode('RectRoi', pos=(600, 200))
fg = fc.createNode('FitGaussian', pos=(800, 100))
con = fc.createNode('Console', pos=(1000, 100))
fc.connectTerminals(lm['data'], ds['data'])
fc.connectTerminals(ds['selected'], imv['image'])
fc.connectTerminals(imv['view'], roi['view'])
fc.connectTerminals(roi['image'], fg['data'])
fc.win.show()
app.exec_()