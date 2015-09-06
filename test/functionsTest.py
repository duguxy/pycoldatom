from init_test import *

import numpy as np
from pycoldatom.functions.fithelper import add_noise, guess_general_2d

class FunctionsTest(unittest.TestCase):
	def test_gaussian(self):
		from pycoldatom.functions.fitclassical import generate_gaussian, fit_gaussian, guess_gaussian, fit_gaussian_result
		
		p, data = generate_gaussian(p0=[1.0, 40, 60, 15, 10, 0.1])
		# p, data = generate_gaussian(p0=[1.0, 4, 6, 5, 3, 0.1], size=(10, 10))
		data = add_noise(data)
		# mask = np.random.random(data.shape)<0.1
		mask = np.zeros_like(data)
		mask[30:50, 50:70] = 1
		data = np.ma.array(data, mask=mask)
		p0 = guess_gaussian(data)		
		p1 = fit_gaussian(data)
		# print('p:', p)
		# print('p0:', p0)
		# print('p1:', p1)
		result, err = fit_gaussian_result(data)
		# print(result)
		np.testing.assert_allclose(p, p1, rtol=1e-2)

	def test_bose_bimodal(self):
		from pycoldatom.functions.fitbosons import generate_bose_bimodal, fit_bose_bimodal, guess_bose_bimodal, fit_bose_bimodal_result

		p, data = generate_bose_bimodal(p0=[1, 1, 40, 60, 30, 20, 10, 10, 0.1])
		p0 = guess_bose_bimodal(data)
		data = add_noise(data)
		p1 = fit_bose_bimodal(data, p0)
		# p1 = p
		# print(data)
		# print('p:', p)
		# print('p0:', p0)
		# print('p1:', p1)
		result, err = fit_bose_bimodal_result(data)
		# print(result)
		np.testing.assert_allclose(p, p1, rtol=1e-1)

	def test_Dfun(self):
		from pycoldatom.functions.fitbosons import bose_bimodal, bose_bimodal_D
		func, dfun = (bose_bimodal, bose_bimodal_D)
		narg = 9
		p0 = np.ones(narg)
		p0[0] = 0.0
		x0 = (0.6, 0.7)
		delta = 1e-5
		dp = np.eye(narg) * delta
		Df = np.array(dfun(x0, *p0))
		f0 = bose_bimodal(x0, *p0)
		Df0 = np.array([func(x0, *(p0 + d)) - f0 for d in dp]) / delta
		np.testing.assert_allclose(Df, Df0, rtol=1e-4)

	def test_polylog(self):
		from pycoldatom.functions.polylog import g2, g2_fp

		x = np.linspace(0, 1.0, 100)
		ref = g2_fp(x)
		result = g2(x)
		# err = ref - result
		# rerr = result / ref
		# rerr[np.isnan(rerr)] = 1
		# print('max:', np.max(err), np.max(rerr))
		# print('min:', np.min(err), np.min(rerr))
		# print('std:', np.std(err), np.std(rerr))
		np.testing.assert_allclose(result, ref, rtol=1e-7, atol=1.5e-7)


if __name__ == '__main__':
	unittest.main()