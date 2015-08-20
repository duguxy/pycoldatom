import os, sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

import unittest
from PyQt5.QtWidgets import QApplication

from pycoldatom.flowchart import Flowchart
