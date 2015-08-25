from random import random

def mock_CLibrary(*args, **kwargs):
	return MockCamera()

class MockCamera:
	def __init__(self):
		print('Mock Camera: __init__')
		self.series = 0

	def __getattr__(self, attr):
		print('Mock Camera: %s' % attr)
		if attr == 'GetAcquisitionProgress':
			return FuncReturn(items={'series': random()*3})
		elif attr == 'GetTemperature':
			return FuncReturn(items={'temperature': -random()*100})
		elif attr == 'GetStatus':
			return FuncReturn(items={'status': 20072} )
		return self.success_call

	def success_call(self, *args):
		print(args)
		return FuncReturn()

class FuncReturn:
	def __init__(self, rval=20002, items={}):
		self.rval = rval
		self.items = items

	def __getitem__(self, i):
		return self.items[i]

	def __call__(self, *args):
		return self

