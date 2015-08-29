from init_test import *

from pycoldatom.functions.fringe import FringeRemove
from pycoldatom.functions.refimages import add_noise

import numpy as np

remover = FringeRemove(trunc=1e-10)
n = 20
dim = 1
w, pos = np.meshgrid(np.random.rand(dim), np.arange(n))
for i in range(10):
	phase, pos = np.meshgrid(np.random.rand(dim), np.arange(n))
	data = np.sin(w*pos + phase).sum(axis=1)
	remover.updateLibrary(data)
	U, s, V = remover.svd_result
	print(remover.rank, np.diagonal(np.dot(U.T, U)))
# print(U.shape, V.shape)
phase, pos = np.meshgrid(np.random.rand(dim), np.arange(n))
data = np.sin(w*pos + phase).sum(axis=1)
mask = np.random.rand(n) < 0.5
data1 = np.ma.array(data, mask=mask)
x, data2 = remover.reconstruct(data1)
print(data)
print(data2)
