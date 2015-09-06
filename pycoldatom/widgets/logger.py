import sys
from PyQt5 import QtCore, QtWidgets, QtWidgets
import logging

class QtHandler(logging.Handler):
	def __init__(self):
		logging.Handler.__init__(self)
	def emit(self, record):
		record = self.format(record)
		if record:
			XStream.stdout().write('%s\n'%record)

class XStream(QtCore.QObject):
	_stdout = None
	_stderr = None
	messageWritten = QtCore.pyqtSignal(str)
	def flush( self ):
		pass
	def fileno( self ):
		return -1
	def write( self, msg ):
		if ( not self.signalsBlocked() ):
			self.messageWritten.emit(msg)
	@staticmethod
	def stdout():
		if ( not XStream._stdout ):
			XStream._stdout = XStream()
			# sys.stdout = XStream._stdout
		return XStream._stdout
	@staticmethod
	def stderr():
		if ( not XStream._stderr ):
			XStream._stderr = XStream()
			# sys.stderr = XStream._stderr
		return XStream._stderr

logger = logging.getLogger('flowchart')
handler = QtHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s]%(levelname)s: (%(name)s) %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class LoggerDialog(QtWidgets.QDialog):
	def __init__( self, parent = None ):
		super().__init__(parent)

		self._console = QtWidgets.QTextBrowser(self)

		layout = QtWidgets.QVBoxLayout()
		layout.addWidget(self._console)
		self.setLayout(layout)

		XStream.stdout().messageWritten.connect( self._console.insertPlainText )
		XStream.stderr().messageWritten.connect( self._console.insertPlainText )

	def showFront(self):
		self.show()
		self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
		self.activateWindow()