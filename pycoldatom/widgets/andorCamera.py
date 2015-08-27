from pyqtgraph.flowchart import Node
from pyclibrary import CParser, CLibrary
import os
import ctypes

import numpy as np

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ctypes import POINTER, c_long

from .cameraSetting_ui import Ui_cameraSettingDialog
from ..utils.qt import stateFunc

class CameraSettingDialog(QDialog, Ui_cameraSettingDialog):
	def __init__(self, *args):
		super().__init__(*args)

		self.setupUi(self)

class AndorCamera(QWidget):
	sigStatusMessage = pyqtSignal(str)
	sigAcquiredData = pyqtSignal(list)
	SETTING_SAVE = ['frameNumberSpinBox', 'frameTransferCheckBox', 'exposureTimeSpinBox',
			'shutterComboBox', 'triggerComboBox', 'hbinSpinBox', 'vbinSpinBox', 
			'preAmplifySlider', 'temperatureSpinBox', 'EMGainCheckBox', 'EMGainSpinBox']
	
	def __init__(self):
		super().__init__()

		self.lastTemp = None

		self.layout = QGridLayout(self)
		
		self.connectButton = QPushButton('Connect', self)
		self.connectButton.clicked.connect(self.onConnect)
		self.layout.addWidget(self.connectButton, 0, 0)

		self.settingsButton = QPushButton('Settings', self)
		self.settingsButton.clicked.connect(self.onSettings)
		self.layout.addWidget(self.settingsButton, 0, 1)
		self.settingsButton.setEnabled(False)

		self.startButton = QPushButton('Start', self)
		self.startButton.clicked.connect(self.onStart)
		self.layout.addWidget(self.startButton, 0, 2)
		self.startButton.setEnabled(False)

		self.progressBar = QProgressBar(self)
		self.layout.addWidget(self.progressBar, 1, 0, 1, 3)
		self.progressBar.setEnabled(False)

		self.tempLayout = QHBoxLayout()
		self.tempLabel = QLabel('OFF', self)
		self.tempLayout.addWidget(self.tempLabel)
		self.coolerCheckBox = QCheckBox('Cooler', self)
		self.tempLayout.addWidget(self.coolerCheckBox)
		self.coolerCheckBox.toggled.connect(self.onCooler)

		self.layout.addLayout(self.tempLayout, 2, 0, 1, 3)
		self.setLayout(self.layout)

		self.camera = None
		self.flowchart = None
		
		self.settingDialog = CameraSettingDialog(self)
		self.settingDialog.setModal(True)
		self.settingDialog.accepted.connect(self.setCamera)

		self.acqTimer = QTimer()
		self.acqTimer.setSingleShot(False)
		self.acqTimer.setInterval(500)
		self.acqTimer.timeout.connect(self.updateProgress)

		self.tempTimer = QTimer()
		self.tempTimer.setSingleShot(False)
		self.tempTimer.setInterval(3000)
		self.tempTimer.timeout.connect(self.updateTemperature)

	def init_drv(self):
		QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
		self.sigStatusMessage.emit('Loading driver...')
		try:
			drv_path = os.environ['ANDORSDK']
		except KeyError:
			raise Exception('Camera driver not found. Check if envionment variable ANDORSDK exist')

		ANDOR_HEADER = os.path.join(drv_path, 'ATMCD32D.H')
		ANDOR_LIB = os.path.join(drv_path, 'atmcd32d.dll')
		ANDOR_CACHE = os.path.join(drv_path, 'ATMCD32D.cache')
		self.header = CParser([ANDOR_HEADER], cache=ANDOR_CACHE, macros={'WINAPI':''})
		self.camera = CLibrary(ANDOR_LIB, self.header, convention='windll')
		self.DRV_SUCCESS = self.camera.DRV_SUCCESS
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
			self.sigStatusMessage.emit('Connecting camera...')
			result = self.camera.Initialize('.').rval
			QApplication.restoreOverrideCursor()

			if result == self.DRV_SUCCESS:
				self.connectButton.setText('Disconnect')
				self.sigStatusMessage.emit('Connected')
				result = self.camera.GetTemperatureRange()
				self.settingDialog.temperatureSpinBox.setRange(result['mintemp'], result['maxtemp'])
				self.settingDialog.temperatureSpinBox.setValue(result['maxtemp'])
				result = self.camera.GetEMGainRange()
				self.settingDialog.EMGainSpinBox.setRange(result['low'], result['high'])
				self.settingsButton.setEnabled(True)
				self.startButton.setEnabled(True)
				self.tempTimer.start()
			else:
				self.sigStatusMessage.emit('Connection Error: %s(%d)' % (self.values[result], result))

		
		elif self.connectButton.text() == 'Disconnect':
			self.tempTimer.stop()
			self.close_drv()
			self.connectButton.setText('Connect')
			self.settingsButton.setEnabled(False)
			self.startButton.setEnabled(False)
			self.sigStatusMessage.emit('Disconnected')

	def onSettings(self):
		self.settingDialog.show()

	def onStart(self):
		if self.startButton.text() == 'Start':
			self.camera.FreeInternalMemory()
			self.startButton.setText('Stop')
			self.progressBar.setRange(0, self.settingDialog.frameNumberSpinBox.value())
			self.progressBar.setValue(0)
			self.progressBar.setEnabled(True)
			self.camera.PrepareAcquisition()
			self.camera.StartAcquisition()
			self.acqTimer.start()
		elif self.startButton.text() == 'Stop':
			self.acqTimer.stop()
			self.camera.AbortAcquisition()
			self.progressBar.setEnabled(False)
			self.startButton.setText('Start')

	def onCooler(self, checked):
		if checked:
			self.camera.CoolerON()
		else:
			self.camera.CoolerOFF()

	def updateProgress(self):
		status = self.camera.GetStatus()['status']
		if status == self.camera.DRV_IDLE:
			self.acquire()
			self.camera.StartAcquisition()
		elif status == self.camera.DRV_ACQUIRING:
			result = self.camera.GetAcquisitionProgress()
			self.progressBar.setValue(result['series'])
		else:
			self.sigStatusMessage.emit('Status Error: %s(%d)' % (self.values[status], status))

	def updateTemperature(self):
		temp = self.camera.GetTemperature()['temperature']
		self.tempLabel.setText('%d ℃' % temp)

		if self.lastTemp is not None:
			if temp > self.lastTemp:
				self.tempLabel.setStyleSheet("QLabel { background-color : red;}")
			elif temp < self.lastTemp:
				self.tempLabel.setStyleSheet("QLabel { background-color : blue;}")
			else:
				self.tempLabel.setStyleSheet("QLabel { background-color : green;}")

		self.lastTemp = temp

	def acquire(self):
		result = self.camera.GetNumberNewImages()
		hbin = self.settingDialog.hbinSpinBox.value()
		vbin = self.settingDialog.vbinSpinBox.value()
		height = int(512/vbin)
		width = int(512/hbin)
		frame_number = self.settingDialog.frameNumberSpinBox.value()
		size = height * width * frame_number
		data = np.empty(size, dtype=np.intc)
		print(result['first'], result['last'])
		if result['first'] == 0 and result['last'] == 0:
			return
		self.camera.GetImages(result['first'], result['last'], data.ctypes.data_as(POINTER(c_long)), size)
		self.sigAcquiredData.emit([arr.reshape(width, height) for arr in np.split(data, frame_number)])

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

		self.camera.SetTemperature(self.settingDialog.temperatureSpinBox.value())
		if self.settingDialog.EMGainCheckBox.isChecked():
			self.camera.SetEMCCDGain(self.settingDialog.EMGainSpinBox.value())
		else:
			self.camera.SetEMCCDGain(0)

	def close(self):
		self.close_drv()

	def saveState(self):
		state = {}
		for settingName in self.SETTING_SAVE:
			for k in stateFunc:
				if settingName.endswith(k):
					break
			else:
				raise Exception('Unknown setting type %s' % settingName)

			setting = getattr(self.settingDialog, settingName)
			state[settingName] = getattr(setting, stateFunc[k][0])()
		return state

	def restoreState(self, state):
		for settingName, settingState in state.items():
			for k in stateFunc:
				if settingName.endswith(k):
					break
			else:
				raise Exception('Unknown setting type %s' % settingName)

			setting = getattr(self.settingDialog, settingName)
			getattr(setting, stateFunc[k][1])(settingState)