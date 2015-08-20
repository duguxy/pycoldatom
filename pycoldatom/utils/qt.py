from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt

def qtstr(qtobj):
	return str(qtobj).replace('PyQt5.', '')

stateFunc = {
	'SpinBox': ('value', 'setValue'),
	'CheckBox': ('isChecked', 'setChecked'),
	'ComboBox': ('currentText', 'setCurrentText'),
	'Slider': ('value', 'setValue')
}

def setBusyCursor():
	QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

def recoverCursor():
	QApplication.restoreOverrideCursor()