import numpy as np
import numpy.linalg as npl
from scipy.linalg import block_diag

from . import incremental_svd
from .incremental_svd import incre_svd

class FringeRemove:
	"""Reconstruct the reference image which is used to remove fringes."""
	def __init__(self, trunc=0.0):
		incremental_svd.trunc = trunc
		self.svd_result = None
		self.rank = 0

		self.reset()

	def updateLibrary(self, image):
		self.svd_result = self.svd.send(image.flatten()[:, np.newaxis])
		U, s, V = self.svd_result
		self.rank = len(s)

	# def reconstruct(self, image):
	# 	U, s, V = self.svd_result
	# 	y = np.ma.compressed(image)[:, np.newaxis]
	# 	if hasattr(image, 'mask'):
	# 		mask = image.mask.flatten()
	# 		q, r = npl.qr(U[np.logical_not(mask)])
	# 		inv = npl.pinv(r * s)
	# 		x = np.dot(V, inv).dot(q.T).dot(y)
	# 	# y = np.ma.filled(image, fill_value=0).flatten()[:, np.newaxis]
	# 	else:
	# 		x = np.dot(V * 1/s, U.T).dot(y)
	# 	return x.flatten(), np.dot(U * s, V.T).dot(x).flatten()

	def reconstruct(self, image):
		U, s, V = self.svd_result
		y = np.ma.compressed(image)[:, np.newaxis]
		if hasattr(image, 'mask'):
			mask = image.mask.flatten()
			U1 = U[np.logical_not(mask)]
		else:
			U1 = U
		x = np.dot(npl.pinv(U1), y)
		return x.flatten(), np.dot(U, x)

	def setTrunc(self, trunc):
		self.trunc = trunc

	def reset(self):
		self.svd = incre_svd()
		next(self.svd)