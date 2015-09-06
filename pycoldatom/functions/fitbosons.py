import logging
logger = logging.getLogger('flowchart.fit_boson')

import numpy as np
from scipy.optimize import leastsq
from .polylog import g2, g2_1, g3_1
from .fithelper import fit_result_wrap, make_fit, make_generate, guess_general_2d, generate_x
from ..utils.exception import Suppressor
from collections import OrderedDict

def bose_thermal(xy, n0, x0, y0, rx, ry, offset):
	x, y = xy
	# print(np.exp(- ((x-x0)/rx)**2 / 2 - ((y-y0)/ry)**2 / 2))
	nt = n0 / g2_1 * g2(np.exp(- ((x-x0)/rx)**2 / 2 - ((y-y0)/ry)**2 / 2)) + offset
	# print(nt)
	return nt

def analyse_bose_thermal(**kwargs):
	a = {}
	ls = locals()
	ls.update(kwargs)
	s = Suppressor((NameError, KeyError), globals(), ls)
	s("a['total'] = g3_1 / g2_1 * 2 * np.pi * n0 * rx * ry")
	
	return a

def bose_thermal_D(xy, n0, x0, y0, rx, ry, offset):
	x, y = xy
	x2 = ((x-x0)/rx)**2 / 2
	y2 = ((y-y0)/ry)**2 / 2
	lg = n0 / g2_1 * np.log(1 - np.exp(- x2 - y2))
	dfun = [
		g2(np.exp(- x2 - y2)) / g2_1, # n0
		-lg * (x-x0) / rx**2, # x0
		-lg * (y-y0) / ry**2, # y0
		-lg * x2 * 2/rx, # rx
		-lg * y2 * 2/ry, # ry
		np.ones_like(x) # offset
	]
	# print(dfun)
	return dfun

def bose_condensed(xy, n0, x0, y0, rx, ry, offset):
	x, y = xy
	nc = 1 - ((x-x0)/rx)**2 - ((y-y0)/ry)**2
	nc = n0 * np.maximum(nc, 0) ** 1.5 + offset
	return nc

def analyse_bose_condensed(**kwargs):
	a = {}
	ls = locals()
	ls.update(kwargs)
	s = Suppressor((NameError, KeyError), globals(), ls)
	s("a['total'] = 2*np.pi/5 * n0 * rx * ry")

	return a

def bose_condensed_D(xy, n0, x0, y0, rx, ry, offset):
	x, y = xy
	x2 = ((x-x0)/rx)**2
	y2 = ((y-y0)/ry)**2
	sq = np.sqrt(np.maximum(1 - x2 - y2, 0.0))
	dfun = [
		sq ** 3, # n0
		n0 * sq * 3 *(x-x0)/rx**2, # x0
		n0 * sq * 3 *(y-y0)/ry**2, # y0
		n0 * sq * x2 * 3/rx, # rx
		n0 * sq * y2 * 3/ry, # ry
		np.ones_like(x) # offset
	]
	return dfun

def bose_bimodal(xy, n0_th, n0_c, x0, y0, rx_th, ry_th, rx_c, ry_c, offset):
	# print(n0_th, n0_c, x0, y0, rx_th, ry_th, rx_c, ry_c, offset)
	return bose_thermal(xy, n0_th, x0, y0, rx_th, ry_th, 0) + \
		bose_condensed(xy, n0_c, x0, y0, rx_c, ry_c, 0) + \
		offset

def bose_bimodal_D(xy, n0_th, n0_c, x0, y0, rx_th, ry_th, rx_c, ry_c, offset):
	x, y = xy
	dt = bose_thermal_D(xy, n0_th, x0, y0, rx_th, ry_th, 0)
	dc = bose_condensed_D(xy, n0_c, x0, y0, rx_c, ry_c, 0)
	dfun = [
		dt[0], # n0_th
		dc[0], # n0_c
		dt[1] + dc[1], # x0
		dt[2] + dc[2], # y0
		dt[3], # rx_t
		dt[4], # ry_t
		dc[3], # rx_c
		dc[4], # ry_c
		np.ones_like(x) # offset
	]
	return dfun

def guess_bose_bimodal(data):
	p_mid = 1 - np.arange(30, 1, -1)**2 * 5e-4
	guess = guess_general_2d(data, p_mid=p_mid)
	
	peak = guess['peak']
	rx = guess['rx']
	ry = guess['ry']
	x0, y0 = np.average([guess['x0'], guess['y0']], axis=1, weights=guess['num'])
	offset = guess['offset']
	p0 = [peak/2, rx[0]/2, rx[0]/2]
	mid = guess['mid']

	def bose_bimodal_simple(x, n0_th, rx_th, rx_c):
		return bose_bimodal((x, 0), n0_th, peak-n0_th, 0, 0, rx_th, 1, rx_c, 1, 0)

	def bose_bimodal_simple_D(x, n0_th, rx_th, rx_c):
		dbb = bose_bimodal_D((x, 0), n0_th, peak-n0_th, 0., 0., rx_th, 1., rx_c, 1., 0)
		return [dbb[0], dbb[4], dbb[6]]

	fit_bose_bimodal_simple = make_fit(bose_bimodal_simple, dfun=bose_bimodal_simple_D)

	px = fit_bose_bimodal_simple(mid, p0=p0, x=rx, factor=0.1)
	py = fit_bose_bimodal_simple(mid, p0=p0, x=ry, factor=0.1)
	guess = [
		(px[0] + py[0]) / 2, # n0_th
		peak - (px[0] + py[0]) / 2, # n0_c
		x0, # x0
		y0, # y0
		px[1], # rx_th
		py[1], # ry_th
		px[2], # rx_c
		py[2], # ry_c
		offset # offset
	]

	# import matplotlib.pyplot as plt
	# print('px:', px)
	# print('py:', py)
	# plt.plot(rx, mid, label='exp_x')
	# plt.plot(rx, bose_bimodal_simple(rx, *px), label='fit_x')
	# plt.plot(ry, mid, label='exp_y')
	# plt.plot(ry, bose_bimodal_simple(ry, *py), label='fit_y')
	# plt.legend()
	# plt.show()
	logger.debug('Initial guess=%s' % guess)
	return guess

def analyse_bose_bimodal(**kwargs):
	a = OrderedDict()
	result = kwargs

	ls = locals()
	ls.update(kwargs)
	s = Suppressor((NameError, KeyError), globals(), ls)
	
	thermal_property = analyse_bose_thermal(
		n0=result['n0_th'],
		rx=result['rx_th'],
		ry=result['ry_th'],
		**kwargs
	)
	for k, v in thermal_property.items():
		a['%s_th' % k] = v

	condensed_property = analyse_bose_condensed(
		n0=result['n0_c'],
		rx=result['rx_c'],
		ry=result['ry_c'],
		**kwargs
	)
	for k, v in condensed_property.items():
		a['%s_c' % k] = v

	s("a['total'] = a['total_c'] + a['total_th']")
	s("a['prop_c'] = a['total_c'] / a['total']")
	s("a['prop_th'] = a['total_th'] / a['total']")

	return a

def fit_bose_bimodal_result(data):
	p0 = guess_bose_bimodal(data)
	p, cov_x, infodict, mesg, ier = fit_bose_bimodal(data, p0, full_output=True)
	result = fit_result_wrap(bose_bimodal, p)
	for x in ['rx_c', 'ry_c', 'rx_th', 'ry_th']:
		result[x] = np.abs(result[x])
	result.update(analyse_bose_bimodal(**result))

	if hasattr(data, 'mask'):
		xy = generate_x(data)
		err = bose_bimodal(xy, *p) - data
	else:
		err = infodict['fvec'].reshape(data.shape)
	return result, err

fit_bose_thermal = make_fit(bose_thermal, dfun=bose_thermal_D)
fit_bose_condensed = make_fit(bose_condensed, dfun=bose_condensed_D)
fit_bose_bimodal = make_fit(bose_bimodal, dfun=bose_bimodal_D, guess=guess_bose_bimodal)

generate_bose_thermal = make_generate(bose_thermal, p0=[1, 50, 50, 20, 20, 0.0])
generate_bose_condensed = make_generate(bose_condensed, p0=[1, 50, 50, 20, 20, 0.0])
generate_bose_bimodal = make_generate(bose_bimodal, p0=[1, 1, 50, 50, 20, 20, 10, 10, 0.0])