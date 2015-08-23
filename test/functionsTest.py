from init_test import *

import numpy as np
from pycoldatom.functions.fithelper import add_noise, guess_general_2d

class FunctionsTest(unittest.TestCase):
	def test_gaussian(self):
		from pycoldatom.functions.fitclassical import generate_gaussian, fit_gaussian, guess_gaussian
		
		print('gaussian')
		p, data = generate_gaussian(p0=[1.0, 40, 60, 15, 10, 0.1])
		data = add_noise(data)
		# mask = np.random.random(data.shape)<0.1
		mask = np.zeros_like(data)
		mask[30:50, 50:70] = 1
		# data = np.ma.array(data, mask=mask)
		p0 = guess_gaussian(data)		
		p1 = fit_gaussian(data)
		print('p:', p)
		print('p0:', p0)
		print('p1:', p1)
		np.testing.assert_allclose(p, p1, rtol=1e-2)

	def _test_bose_thermal(self):
		from pycoldatom.functions.fitbosons import generate_bose_thermal, fit_bose_thermal
		from pycoldatom.functions.fitclassical import guess_gaussian
		p, data = generate_bose_thermal(p0=[1.0, 40, 60, 15, 10, 0.1])

		# data = add_noise(data)
		p0 = p
		p1 = fit_bose_thermal(data, p0)
		print(p, p1)
		np.testing.assert_allclose(p, p1, rtol=1e-2)

	def test_bose_bimodal(self):
		from pycoldatom.functions.fitbosons import generate_bose_bimodal, guess_bose_bimodal

		print('bose_bimodal')
		p, data = generate_bose_bimodal(p0=[1, 1, 40, 60, 25, 20, 10, 10, 0.1])
		p0 = guess_bose_bimodal(data)
		# print(data)
		print('p:', p)
		print('p0:', p0)
		# print('p1:', p1)

if __name__ == '__main__':
	unittest.main()