import cv2
import numpy as np
from scipy.optimize import leastsq

from .fithelper import make_residual_2d, fit_result_wrap

def guess_gaussian(image):
	m = cv2.moments(image)
	m00 = m['m00']
	m01 = m['m01']
	m10 = m['m10']
	m11 = m['m11']
	m20 = m['m20']
	m02 = m['m02']

	x, y = image.shape
	s0 = x * y
	sx = s0 * (x-1) / 2
	sy = s0 * (y-1) / 2
	sx2 = sx * (2*x-1) / 3
	sy2 = sy * (2*x-1) / 3

	A = (sy*m00 - s0*m01) * (sx*m00 - s0*m10) / (sx*sy*m00 - s0*sy*m10 - s0*sx*m01 +s0*s0*m11)
	B = (m00 - A) / s0

	x0 = (m10 - B * sx) / A
	y0 = (m01 - B * sy) / A

	mu20 = (m20 - B*sx2) - 2*x0*(m10 - B*sx) + x0*x0*(m00 - B*s0)
	if mu20 > 0:
		rx = np.sqrt(2 * mu20 / A)
	else:
		rx = x / 10
	
	mu02 = (m02 - B*sy2) - 2*y0*(m01 - B*sy) + y0*y0*(m00 - B*s0)
	if mu02 > 0:
		ry = np.sqrt(2 * mu02 / A)
	else:
		ry = y / 10

	n0 = A / (np.pi*rx*ry)
	return [n0, x0, y0, rx, ry, B]

def gaussian(xy, n0, x0, y0, rx, ry, offset):
	x, y = xy
	g = n0*np.exp(-(x-x0)**2/(2*rx**2)-(y-y0)**2/(2*ry**2)) + offset
	return g

def gaussian_Dfun(xy, n0, x0, y0, rx, ry, offset):
	x, y = xy
	x2 = -(x-x0)**2/(2*rx**2)
	y2 = -(y-y0)**2/(2*ry**2)
	exy = np.exp(x2 + y2)
	dg = [
		exy, # n0
		n0 * exy * 2*(x-x0)/rx**2, # x0
		n0 * exy * 2*(y-y0)/ry**2, # y0
		n0 * exy * -x2 * 2/rx, # rx
		n0 * exy * -y2 * 2/ry, # ry
		np.ones_like(x) # offset
	]
	return dg

def fit_gaussian(data, weight=None, p0=None, full_output=False):
	residual, Dresidual = make_residual_2d(gaussian, data, weight=weight, Dfun=gaussian_Dfun)
	p0 = guess_gaussian(data)
	result = leastsq(residual, p0, Dfun=Dresidual, col_deriv=1, full_output=full_output)
	if full_output:
		return result
	else:
		x, ier = result
		if ier not in [1, 2, 3, 4]:
			print('Solution not Found')
		return x

def fit_gaussian_node(data, pos):
	p, cov_x, infodict, mesg, ier = fit_gaussian(data, full_output=True)
	result = fit_result_wrap(gaussian, p)
	if pos is not None:
		result['x0'] += pos.x()
		result['y0'] += pos.y()
	err = infodict['fvec'].reshape(data.shape)
	return result, err


def fit_gaussian_IRLS(data, p0=None, niter=3, wmin=1e-3):
	weight = None
	for i in range(niter):
		p0, cov_x, infodict, mesg, ier = fit_gaussian(data, weight=weight, p0=p0, full_output=True)
		weight = infodict['fvec']
		weight[weight < wmin] = wmin
		weight = 1 / weight
	return p0

def generate_gaussian(p0=[1.0, 50, 50, 10, 10, 0.0], size=[100, 100], rand=0.1):
	p = p0 * (1 + 2 * rand * (np.random.rand(len(p0)) - 0.5))
	x, y = np.mgrid[:size[0], :size[1]]
	g = gaussian((x, y), *p)
	return np.array(p), g

def test():
	from refimages import add_noise

	p, data = generate_gaussian(p0=[1.0, 50, 50, 10, 10, 0.1])
	# data = add_noise(data, ampl=0.1, noisetype='fringes', frigneargs=[0, 0.1, 30, ])
	# data += 0.3 * np.random.random(data.shape) / (1+data)
	print((fit_gaussian(data) - p) / p)
	print((fit_gaussian_IRLS(data) - p) / p)

if __name__ == '__main__':
	for i in range(10):
		print('.')
		test()