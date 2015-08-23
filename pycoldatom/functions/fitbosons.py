import numpy as np
from scipy.optimize import leastsq
from .polylog import g2
from .fithelper import fit_result_wrap, make_fit, make_generate, guess_general_2d

def bose_thermal(xy, n0, x0, y0, rx, ry, offset):
	x, y = xy
	nt = n0 * g2(np.exp(- ((x-x0)/rx)**2 / 2 - ((y-y0)/ry)**2 / 2)) + offset
	return nt

def bose_thermal_D(xy, n0, x0, y0, rx, ry, offset):
	x, y = xy
	x2 = ((x-x0)/rx)**2 / 2
	y2 = ((y-y0)/ry)**2 / 2
	lg = n0 * np.log(1 - np.exp(1- x2 - y2))
	dfun = [
		g2(np.exp(- x2 - y2)), # n0
		lg * (x-x0) / rx**2, # x0
		lg * (y-y0) / ry**2, # y0
		lg * (x-x0) * x2 * 2/rx, # rx
		lg * (y-y0) * y2 * 2/ry, # ry
		np.ones_like(x) # offset
	]
	return dfun

def guess_bose_thermal(data):
	guess = guess_general_2d(data)

def bose_condensed(xy, n0, x0, y0, rx, ry, offset):
	x, y = xy
	nc = 1 - ((x-x0)/rx)**2 - ((y-y0)/ry)**2
	nc = n0 * np.maximum(nc, 0) ** 1.5 + offset
	return nc

def bose_condensed_D(xy, n0, x0, y0, rx, ry, offset):
	x, y = xy
	x2 = ((x-x0)/rx)**2
	y2 = ((y-y0)/ry)**2
	sq = np.sqrt(np.maximum(1 - x2 - y2, 0.0))
	dfun = [
		sq ** 3, # n0
		n0 * sq * 3/2*(x-x0)/rx**2, # x0
		n0 * sq * 3/2*(y-y0)/ry**2, # y0
		n0 * sq * x2 * 3/rx, # rx
		n0 * sq * y2 * 3/ry, # ry
		np.ones_like(x) # offset
	]
	return dfun

def bose_bimodal(xy, n0_th, n0_c, x0, y0, rx_th, ry_th, rx_c, ry_c, offset):
	return bose_thermal(xy, n0_th, x0, y0, rx_th, ry_th, 0) + \
		bose_condensed(xy, n0_c, x0, y0, rx_c, ry_c, 0) + \
		offset

def bose_biomodal_D(xy, n0_th, n0_c, x0, y0, rx_th, ry_th, rx_c, ry_c, offset):
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

def bose_bimodal_simple(x, n0_th, n0_c, rx_th, rx_c):
	return bose_bimodal((x, 0), n0_th, n0_c, 0, 0, rx_th, 1, rx_c, 1, 0)

def bose_bimodal_simple_D(x, n0_th, n0_c, rx_th, rx_c):
	bbd = bose_biomodal_D((x, 0), n0_th, n0_c, 0, 0, rx_th, 1, rx_c, 1, 0)
	return [bbd[0], bbd[1], bbd[3], bbd[5]]

fit_bose_bimodal_simple = make_fit(bose_bimodal_simple) # dfun=bose_bimodal_simple_D)

def guess_bose_bimodal(data):
	p_mid = 1 - np.arange(30, 1, -1)**2 * 5e-4
	guess = guess_general_2d(data, p_mid=p_mid)
	
	peak = guess['peak']
	rx = np.array(guess['rx'])
	p0 = [peak/2, peak/2, rx[0]/2, rx[0]/2]
	mid = np.array(guess['mid'])
	p = fit_bose_bimodal_simple(mid, p0=p0)
	print(p)
	dmid = np.diff(guess['mid'])

	drx = np.diff(guess['rx'])
	d2rx = np.diff(drx) / 2
	curv_x = np.diff(dmid / drx) / d2rx
	# print(guess['rx'])
	# print(guess['mid'])
	# print(dmid / drx)
	# print(curv_x)
	# print(guess['offset'])
	import matplotlib.pyplot as plt
	plt.plot(rx, mid)
	plt.plot(rx, bose_bimodal_simple(rx, *p))
	plt.plot(rx, bose_bimodal_simple(rx, *p0))
	plt.show()



fit_bose_thermal = make_fit(bose_thermal, dfun=bose_thermal_D)
fit_bose_condensed = make_fit(bose_condensed, dfun=bose_condensed_D)
fit_bose_bimodal = make_fit(bose_bimodal, dfun=bose_biomodal_D)

generate_bose_thermal = make_generate(bose_thermal, p0=[1, 50, 50, 20, 20, 0.0])
generate_bose_condensed = make_generate(bose_condensed, p0=[1, 50, 50, 20, 20, 0.0])
generate_bose_bimodal = make_generate(bose_bimodal, p0=[1, 1, 50, 50, 20, 20, 10, 10, 0.0])