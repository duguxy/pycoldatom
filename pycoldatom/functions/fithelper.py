import numpy as np
import inspect
from collections import OrderedDict

def make_residual_2d(func, data, weight=None, Dfun=None):
	shape = data.shape
	x, y = np.mgrid[:shape[0], :shape[1]]

	if weight is None:
		weight = 1

	def residual(p):
		err = func((x, y), *p) - data
		return err.ravel()*weight

	if Dfun is None:
		return residual

	def Dresidual(p):
		df = [d.ravel()*weight for d in Dfun((x, y), *p)]
		return df

	return residual, Dresidual

class FitResult(OrderedDict):
	pass

def fit_result_wrap(func, p):
	return dict(zip(inspect.getfullargspec(func)[0][1:], p))