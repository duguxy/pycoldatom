from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import zmq

class CiceroListener(QThread):
	sigCiceroRunning = pyqtSignal(list)
	sigCiceroListvalue = pyqtSignal(list)
	sigCiceroTime = pyqtSignal(list)

	def __init__(self, port=7854):
		super(CiceroListener, self).__init__()
		
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.SUB)

		self.port = port

		self.socket.connect ("tcp://192.168.1.200:%d" % self.port)
		self.topicfilter = b"Cicero: "
		self.socket.setsockopt(zmq.SUBSCRIBE, self.topicfilter)

		self.keep_running = False

		self.commands = {}

	def run(self):
		while(self.keep_running):
			message = self.socket.recv().decode(encoding="ascii")
			message = message[len(self.topicfilter):]
			command = message.split(',')
			self.commands[command[0]] = command[1:]
			if command[0] == 'run':
				self.sigCiceroRunning.emit(command[1:])
			elif command[0] == 'listvalue':
				self.sigCiceroListvalue.emit(command[1:])
			elif command[0] == 'time':
				self.sigCiceroTime.emit(command[1:])

if __name__ == '__main__':
	app = QApplication([])

	listener = CiceroListener(7854)
	def print_sig(command):
		print(listener.commands)

	listener.sigCiceroTime.connect(print_sig)
	listener.sigCiceroListvalue.connect(print_sig)
	listener.sigCiceroRunning.connect(print_sig)

	listener.keep_running = True
	listener.start()

	app.exec_()
