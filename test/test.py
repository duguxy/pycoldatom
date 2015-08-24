
from init_test import *

from pycoldatom.functions.polylog import g2, g2_old
from sympy.mpmath import polylog

import matplotlib.pyplot as plt
import numpy as np

import cProfile

def plot():
	x = np.linspace(0, 0.1, 10000)
	def _g2_ref(x):
		return polylog(2, x)
	g2_ref = np.vectorize(_g2_ref)
	ref = g2_ref(x)
	cProfile.runctx('g2(x)', globals(), locals())
	res = g2(x)
	cProfile.runctx('g2_old(x)', globals(), locals())
	res2 = g2_old(x)
	err = res - ref
	err2 = res2 - ref
	# print(res<0)
	print(err.std())
	plt.plot(x, err, label='err1')
	plt.plot(x, err2, label='err2')
	plt.legend()
	plt.show()

# x = np.linspace(0.999, 1.0, 10000)
# res = g2(x)
# # print((res<0).any())
# plt.plot(x, res)
# plt.show()

# plot()
print(g2(1))