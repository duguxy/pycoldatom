from pyqtgraph.flowchart import Node
from pyclibrary import CParser, CLibrary
import os
import ctypes

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtQuick import QQuickView, QQuickItem

from .cameraSetting_ui import Ui_cameraSettingDialog
from ...utils.qt import stateFunc

class CameraSettingDialog(QDialog, Ui_cameraSettingDialog):
	def __init__(self):
		super().__init__()

		self.setupUi(self)

class AndorNode(Node):
	nodeName = "Andor Camera"
	nodePaths = [('Camera',)]

	SETTING_SAVE = ['frameNumberSpinBox', 'frameTransferCheckBox', 'exposureTimeSpinBox',
			'shutterComboBox', 'triggerComboBox', 'hbinSpinBox', 'vbinSpinBox', 
			'preAmplifySlider']

	def __init__(self, name, **kwargs):
		terminals = {
			'image': {'io': 'out'}
		}
		super().__init__(name, terminals=terminals, **kwargs)

		self.panel = QWidget()
		self.layout = QGridLayout(self.panel)
		
		self.connectButton = QPushButton('Connect')
		self.connectButton.clicked.connect(self.onConnect)
		self.layout.addWidget(self.connectButton)

		self.settingsButton = QPushButton('Settings')
		self.settingsButton.clicked.connect(self.onSettings)
		self.layout.addWidget(self.settingsButton)
		self.settingsButton.setEnabled(False)

		self.panel.setLayout(self.layout)

		self.camera = None
		self.flowchart = None
		self.statusBar = None
		
		self.settingDialog = CameraSettingDialog()
		self.settingDialog.setModal(True)
		self.settingDialog.accepted.connect(self.setCamera)

		

	def init_drv(self):
		QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
		self.statusBar.showMessage('Loading driver...')
		try:
			drv_path = os.environ['ANDORSDK']
		except KeyError:
			raise Exception('Camera driver not found. Check if envionment variable ANDORSDK exist')

		ANDOR_HEADER = os.path.join(drv_path, 'ATMCD32D.H')
		ANDOR_LIB = os.path.join(drv_path, 'atmcd32d.dll')
		ANDOR_CACHE = os.path.join(drv_path, 'ATMCD32D.cache')
		self.header = CParser([ANDOR_HEADER], cache=ANDOR_CACHE, macros={'WINAPI':''})
		self.camera = CLibrary(ANDOR_LIB, self.header, convention='windll')
		self.DRV_SUCCESS = self.header.defs['values']['DRV_SUCCESS']
		self.values = dict((v, k) for k, v in self.header.defs['values'].items())
		
		QApplication.restoreOverrideCursor()

	def close_drv(self):
		if self.camera is not None:
			result = self.camera.ShutDown().rval

	def onConnect(self):
		if self.connectButton.text() == 'Connect':
			if self.camera is None:
				self.init_drv()

			QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
			self.statusBar.showMessage('Connecting camera...')
			result = self.camera.Initialize('.').rval
			QApplication.restoreOverrideCursor()

			if result == self.DRV_SUCCESS:
				self.connectButton.setText('Disconnect')
				self.statusBar.showMessage('Connected')
				self.settingsButton.setEnabled(True)
			else:
				self.statusBar.showMessage('Connection Error %s' % self.values)
		
		elif self.connectButton.text() == 'Disconnect':
			self.close_drv()
			self.connectButton.setText('Connect')
			self.settingsButton.setEnabled(False)
			self.statusBar.showMessage('Disconnected')

	def onSettings(self):
		self.settingDialog.show()

	# def init_settingsui(self):
	# 	QML_FILENAME = os.path.join(os.path.dirname(__file__), 'CameraSettings.qml')
	# 	self.settingDialog = QQuickView()
	# 	self.settingDialog.setSource(QUrl.fromLocalFile(QML_FILENAME))
	# 	self.settingDialog.setResizeMode(QQuickView.SizeRootObjectToView)

	# 	self.settings = self.settingDialog.rootObject()
	# 	# self.settings.okayClicked.connect(self.output)
	# 	okaybutton = self.settings.findChild(QQuickItem, 'Button')
	# 	okaybutton.onClicked.connect(self.output)

	def setCamera(self):
		hbin = self.settingDialog.hbinSpinBox.value()
		vbin = self.settingDialog.vbinSpinBox.value()
		exposureTime = ctypes.c_float(self.settingDialog.exposureTimeSpinBox.value()/1000.0)
		
		if self.settingDialog.frameTransferCheckBox.isChecked():
			self.camera.SetAcquisitionMode(4)
			self.camera.SetFastKinetics(512, 2, exposureTime, 4, hbin, vbin)
		else:
			self.camera.SetAcquisitionMode(3)
			self.camera.SetImage(hbin, vbin, 1, 512, 1, 512)
			self.camera.SetExposureTime(exposureTime)

		framenumber = self.settingDialog.frameNumberSpinBox.value()
		self.camera.SetNumberKinetics(framenumber)

		trigger = self.settingDialog.triggerComboBox.currentText()
		trigger_dict = {
			'Internal': 0,
			'External': 1
		}
		self.camera.SetTriggerMode(trigger_dict[trigger])

		shutter = self.settingDialog.shutterComboBox.currentText()
		shutter_dict = {
			'Auto': 0,
			'Open': 1,
			'Close': 2
		}
		self.camera.SetShutter(1, shutter_dict[shutter], 27, 27)

		preamp = self.settingDialog.preAmplifySlider.value()
		self.camera.SetPreAmpGain(preamp)

	def output(self):
		print('aaa')

	def ctrlWidget(self):
		return self.panel

	def close(self):
		self.close_drv()
		super().close()

	def saveState(self):
		state = {}
		for settingName in self.SETTING_SAVE:
			for k in stateFunc:
				if settingName.endswith(k):
					break
			else:
				raise Exception('Unknown setting type')

			setting = getattr(self.settingDialog, settingName)
			state[settingName] = getattr(setting, stateFunc[k][0])()
		return state

	def restoreState(self, state):
		for settingName, settingState in state.items():
			for k in stateFunc:
				if settingName.endswith(k):
					break
			else:
				raise Exception('Unknown setting type')

			setting = getattr(self.settingDialog, settingName)
			getattr(setting, stateFunc[k][1])(settingState)

nodelist = [AndorNode]