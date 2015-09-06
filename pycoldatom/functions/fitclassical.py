import numpy as np
from scipy.optimize import leastsq
from ..utils.exception import Suppressor
from .fithelper import make_fit, make_generate, fit_result_wrap, generate_x, guess_general_2d, mask_bound
import logging

logger = logging.getLogger('flowchart.fit_gaussian')
# def guess_gaussian2(data):
# 	if hasattr(data, 'mask'):
# 		x0, x1, y0, y1 = mask_bound(data.mask)
# 	else:
# 		x1, y1 = data.shape
# 		x0 = 0
# 		y0 = 0
# 	print(x0, x1, y0, y1)
# 	return [1, (x0+x1)/2, (y0+y1)/2, (x1-x0)/4, (y1-y0)/4, 0]

def guess_gaussian(data):
	guess = guess_general_2d(data, p_mid=[0.8, 0.9])

	n0 = guess['peak']
	offset = guess['offset']
	x0 = guess['x0'][0]
	y0 = guess['y0'][0]
	a = np.sqrt(2 * np.log(n0 / guess['mid'][0]))
	rx = guess['rx'][0] / a
	ry = guess['ry'][0] / a
	p0 = [n0, x0, y0, rx, ry, offset]
	logger.debug('Initial guess=%s' % p0)
	return p0

def gaussian(xy, n0, x0, y0, rx, ry, offset):
	x, y = xy
	g = n0*np.exp(-(x-x0)**2/(2*rx**2)-(y-y0)**2/(2*ry**2)) + offset
	return g

def gaussian_D(xy, n0, x0, y0, rx, ry, offset):
	x, y = xy
	x2 = (x-x0)**2/(2*rx**2)
	y2 = (y-y0)**2/(2*ry**2)
	exy = np.exp(-x2 - y2)
	dfun = [
		exy, # n0
		n0 * exy * (x-x0)/rx**2, # x0
		n0 * exy * (y-y0)/ry**2, # y0
		n0 * exy * x2 * 2/rx, # rx
		n0 * exy * y2 * 2/ry, # ry
		np.ones_like(x) # offset
	]
	return dfun

fit_gaussian = make_fit(gaussian, dfun=gaussian_D, guess=guess_gaussian)

def fit_gaussian_result(data):
	p0 = guess_gaussian(data)
	p, cov_x, infodict, mesg, ier = fit_gaussian(data, p0, full_output=True)
	result = fit_result_wrap(gaussian, p)
	for x in ['rx', 'ry']:
		result[x] = np.abs(result[x])

	result.update(analyse_gaussian(**result))

	if hasattr(data, 'mask'):
		xy = generate_x(data)
		err = gaussian(xy, *p) - data
	else:
		err = infodict['fvec'].reshape(data.shape)
	return result, err

def fit_gaussian_IRLS(data, p0, niter=3, wmin=1e-3):
	for i in range(niter):
		p0, cov_x, infodict, mesg, ier = fit_gaussian(data, p0, weight=weight, full_output=True)
		weight = infodict['fvec']
		weight[weight < wmin] = wmin
		weight = 1 / weight
	return p0

def analyse_gaussian(**kwargs):
	a = {}
	ls = locals()
	ls.update(kwargs)
	s = Suppressor((NameError, KeyError), globals(), ls)
	s("a['total'] = 2 * np.pi * n0 * rx * ry")

	return a

generate_gaussian = make_generate(gaussian, p0=[1.0, 50, 50, 10, 10, 0.0])