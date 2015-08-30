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

class AndorCamera(QObject):
	sigStatusMessage = pyqtSignal(str)
	sigAcquiredData = pyqtSignal(list)
	SETTING_SAVE = ['frameNumberSpinBox', 'frameTransferCheckBox', 'exposureTimeSpinBox',
			'shutterComboBox', 'triggerComboBox', 'hbinSpinBox', 'vbinSpinBox', 
			'preAmplifySlider', 'temperatureSpinBox', 'EMGainCheckBox', 'EMGainSpinBox']
	
	def __init__(self):
		super().__init__()

		self.lastTemp = None
		self.shot_mode = None
		self.frames_to_shot = 0
		self.frame_number = 0

		self.frames = []
		
		self.progressBar = QProgressBar()
		self.progressBar.setEnabled(False)

		self.tempLabel = QLabel('OFF')

		self.toolbar = QToolBar('Camera')
		self.connectAction = QAction('Connect', self.toolbar, triggered=self.onConnect)
		self.toolbar.addAction(self.connectAction)
		self.settingsAction = QAction('Settings', self.toolbar, triggered=self.onSettings)
		self.settingsAction.setEnabled(False)
		self.toolbar.addAction(self.settingsAction)
		self.startAction = QAction('Start', self.toolbar, triggered=self.onStart)
		self.startAction.setEnabled(False)
		self.toolbar.addAction(self.startAction)

		self.camera = None
		self.flowchart = None
		
		self.settingDialog = CameraSettingDialog()
		self.settingDialog.setModal(True)
		self.settingDialog.accepted.connect(self.setCamera)

		self.acqTimer = QTimer()
		self.acqTimer.setSingleShot(False)
		self.acqTimer.setInterval(200)
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
		if self.connectAction.text() == 'Connect':
			if self.camera is None:
				self.init_drv()

			QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
			self.sigStatusMessage.emit('Connecting camera...')
			result = self.camera.Initialize('.').rval
			QApplication.restoreOverrideCursor()

			if result == self.DRV_SUCCESS:
				self.connectAction.setText('Disconnect')
				self.sigStatusMessage.emit('Connected')
				result = self.camera.GetTemperatureRange()
				self.settingDialog.temperatureSpinBox.setRange(result['mintemp'], result['maxtemp'])
				self.settingDialog.temperatureSpinBox.setValue(result['maxtemp'])
				result = self.camera.GetEMGainRange()
				self.settingDialog.EMGainSpinBox.setRange(result['low'], result['high'])
				self.settingsAction.setEnabled(True)
				self.startAction.setEnabled(True)
				self.tempTimer.start()
				self.setCamera()
			else:
				self.sigStatusMessage.emit('Connection Error: %s(%d)' % (self.values[result], result))

		
		elif self.connectAction.text() == 'Disconnect':
			self.tempTimer.stop()
			self.close_drv()
			self.connectAction.setText('Connect')
			self.settingsAction.setEnabled(False)
			self.startAction.setEnabled(False)
			self.sigStatusMessage.emit('Disconnected')

	def onSettings(self):
		self.settingDialog.show()

	def onStart(self):
		if self.startAction.text() == 'Start':
			self.connectAction.setEnabled(False)
			self.settingsAction.setEnabled(False)
			self.camera.FreeInternalMemory()
			self.startAction.setText('Stop')
			self.progressBar.setRange(0, self.settingDialog.frameNumberSpinBox.value())
			self.progressBar.setValue(0)
			self.progressBar.setEnabled(True)
			self.camera.PrepareAcquisition()
			self.camera.StartAcquisition()
			self.frames_to_shot = self.frame_number
			self.frames = []
			self.acqTimer.start()
		elif self.startAction.text() == 'Stop':
			self.connectAction.setEnabled(True)
			self.settingsAction.setEnabled(True)
			self.acqTimer.stop()
			self.camera.AbortAcquisition()
			self.progressBar.setEnabled(False)
			self.startAction.setText('Start')

	def updateProgress(self):
		status = self.camera.GetStatus()['status']
		if self.shot_mode == 'Kinetics':
			if status == self.camera.DRV_IDLE:
				self.acquire(self.frame_number)
				self.sigAcquiredData.emit(list(self.frames))
				self.frames = []
				self.camera.StartAcquisition()
			elif status == self.camera.DRV_ACQUIRING:
				result = self.camera.GetAcquisitionProgress()
				self.progressBar.setValue(result['series'])
			else:
				self.sigStatusMessage.emit('Status Error: %s(%d)' % (self.values[status], status))
		elif self.shot_mode == 'FastKinetics':
			if status == self.camera.DRV_IDLE:
				self.frames_to_shot -= 2
				self.acquire(2)
				if self.frames_to_shot == 0:
					self.sigAcquiredData.emit(list(self.frames))
					self.frames_to_shot = self.frame_number
					self.frames = []
				self.camera.StartAcquisition()
				self.progressBar.setValue(self.frame_number - self.frames_to_shot)

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

	def acquire(self, frame_number):
		result = self.camera.GetNumberAvailableImages()
		if result['first'] == 0 and result['last'] == 0:
			return
		hbin = self.settingDialog.hbinSpinBox.value()
		vbin = self.settingDialog.vbinSpinBox.value()
		height = int(512/vbin)
		width = int(512/hbin)
		# frame_number = self.frame_number
		size = height * width * frame_number
		data = np.empty(size, dtype=np.intc)
		self.camera.GetImages(result['first'], result['last'], data.ctypes.data_as(POINTER(c_long)), size)
		self.frames.extend([arr.reshape(width, height) for arr in np.split(data, frame_number)])
			

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
		framenumber = self.settingDialog.frameNumberSpinBox.value()
		self.frame_number = framenumber

		if self.settingDialog.frameTransferCheckBox.isChecked():
			self.shot_mode = 'FastKinetics'
			self.camera.SetAcquisitionMode(4)
			self.camera.SetFastKinetics(512, 2, exposureTime, 4, hbin, vbin)
		else:
			self.shot_mode = 'Kinetics'
			self.camera.SetAcquisitionMode(3)
			self.camera.SetImage(hbin, vbin, 1, 512, 1, 512)
			self.camera.SetExposureTime(exposureTime)
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

		if self.settingDialog.coolerCheckBox.isChecked():
			self.camera.CoolerON()
			self.camera.SetTemperature(self.settingDialog.temperatureSpinBox.value())
		else:
			self.camera.CoolerOFF()
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