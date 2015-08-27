import sys
from init_flowchart import *

def main():
	app = QApplication([])
	fc = Flowchart()

	if len(sys.argv) > 1:
		fc.loadFile(sys.argv[1])

	fc.win.show()
	app.exec_()

if __name__ == '__main__':
	main()