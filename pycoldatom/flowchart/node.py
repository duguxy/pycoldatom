import pyqtgraph.flowchart as pgfc
import threading

def background_node(cls):
	def process(self, *args, **kwargs):
		t = threading.Thread(target=cls.process, args=args, kwargs=kwargs)