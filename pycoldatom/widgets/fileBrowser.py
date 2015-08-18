from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class FileBrowser(QTreeView):
	def __init__(self, *args, rootpath=None, **kwargs):
		super().__init__(*args, **kwargs)

		self.filemodel = QFileSystemModel()
		self.setModel(self.filemodel)
		self.filemodel.setRootPath(rootpath)