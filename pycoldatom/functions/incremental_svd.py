import numpy as np
import numpy.linalg as npl
from scipy.linalg import block_diag

trunc = 0.0

def incre_svd():
	""" Incremental SVD generator, see 
	Matthew Brand, Incremental singular value decomposition of uncertain data with missing values
	http://www.cs.wustl.edu/~zhang/teaching/cs517/Spring12/CourseProjects/incremental%20svd%20missing%20value.pdf
	"""

	c = yield
	s = np.array([npl.norm(c.astype(float))])
	# s = npl.norm(c.astype(float), axis=1)
	U0 = c / s
	Up = 1.0
	V0 = 1.0
	Vp = 1.0
	Vpi = 1.0

	while True:
		r = len(s)
		U = np.dot(U0, Up)
		V = np.dot(V0, Vp)
		c = yield U, s, V
		if c is None:
			continue

		I = np.identity(r)
		O = np.zeros(r)

		l = np.dot(U.T, c)
		j = c - np.dot(U, l)
		k = npl.norm(j)
		j /= k
		
		print(k)
		if k < trunc:
			k = 0
		
		Q = block_diag(np.diag(s), k)
		Q[:r, -1:] = l
		A, s, B = npl.svd(Q, full_matrices=False)
		B = B.T

		if k < trunc:
			s = s[:-1]
			Up = np.dot(Up, A[:-1, :-1])

			W, w = np.vsplit(B[:, :-1], [r])
			Wi = (I + np.dot(w.T, w) / (1 - np.dot(w, w.T))).dot(W.T)

			Vp = np.dot(Vp, W)
			Vpi = np.dot(Wi, Vpi)
			V0 = np.vstack((V0, np.dot(w, Vpi)))

		else:
			Up = block_diag(Up, 1).dot(A)
			U0 = np.hstack((U0, j))
			V0 = block_diag(V0, 1)
			Vp = np.dot(block_diag(Vp, 1), B)
			Vpi = np.dot(B.T, block_diag(Vpi, 1))