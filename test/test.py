from mockCamera import mock_CLibrary
from init_test import *

from PyQt5.QtWidgets import QApplication
from pycoldatom.flowchart import Flowchart

from unittest.mock import patch

# import logging
# import sys

# root = logging.getLogger()
# root.setLevel(logging.DEBUG)

# ch = logging.StreamHandler(sys.stdout)
# ch.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch.setFormatter(formatter)
# root.addHandler(ch)

@patch('pyclibrary.CLibrary', mock_CLibrary)
def test():
	app = QApplication([])
	fc = Flowchart()

	lena = fc.createNode('Andor Camera', pos=(0, 100))
	fc.win.show()
	app.exec_()

if __name__ == '__main__':
	test()