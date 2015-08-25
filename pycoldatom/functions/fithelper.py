import numpy as np
import inspect
from collections import OrderedDict
from scipy.optimize import leastsq

def guess_general_2d(data, p_max=1-3e-4, p_min=0.2, p_mid=[0.75, 0.8]):
	result = {}

	if hasattr(data, 'mask'):
		x0, x1, y0, y1 = mask_bound(data)
		data = data[x0:x1, y0:y1]
		n = data.count()
		data_flat = data.flatten().filled(np.inf)		
	else:
		n = data.size
		data_flat = data.flatten()
		x0 = 0.0
		y0 = 0.0

	n_max = int(n * p_max)
	n_min = int(n * p_min)
	n_mid = [int(n * p) for p in p_mid]

	ind_sorted = np.argpartition(data_flat, [n_min] + n_mid + [n_max])
	ind_max = np.unravel_index(ind_sorted[n_max:n], data.shape)
	ind_min = np.unravel_index(ind_sorted[:n_min], data.shape)
	ind_mid = [np.unravel_index(arr, data.shape) for arr in np.split(ind_sorted, n_mid)[1:-1] if arr.size]

	sq2 = np.sqrt(2)

	offset = data[ind_min].mean()
	result['offset'] = offset
	result['peak'] = data[ind_max].mean() - offset
	for k in ['x0', 'y0', 'rx', 'ry', 'mid', 'num']:
		result[k] = np.zeros(len(ind_mid))
	for i, arr in enumerate(ind_mid):
		coord_x, coord_y = arr
		result['x0'][i] = coord_x.mean() + x0
		result['y0'][i] = coord_y.mean() + y0
		result['rx'][i] = coord_x.std() * sq2
		result['ry'][i] = coord_y.std() * sq2
		result['mid'][i] = data[arr].mean() - offset
		result['num'][i] = len(coord_x)
	return result

def generate_x(data):
	x = np.mgrid[[slice(s) for s in data.shape]]

	if hasattr(data, 'mask'):
		x = [np.ma.array(x0, mask=data.mask) for x0 in x]

	return x

def mask_bound(mask):
	x = np.all(mask, axis=1)
	y = np.all(mask, axis=0)
	nx, ny = mask.shape

	return (np.argmin(x), nx-np.argmin(x[::-1]), np.argmin(y), ny-np.argmin(y[::-1]))

def make_residual(func, data, weight=None, Dfun=None, x=None):
	if x is None:
		x = generate_x(data)

	if len(data.shape) > 1:
		x = [np.ma.compressed(x0) for x0 in x]
	else:
		x = np.ma.compressed(x)
	data = np.ma.compressed(data)

	if weight is None:
		weight = 1

	def residual(p):
		err = func(x, *p) - data
		# print((err**2).sum())
		return err*weight

	if Dfun is None:
		return residual, None

	def Dresidual(p):
		df = [d*weight for d in Dfun(x, *p)]
		return df

	return residual, Dresidual

def make_fit(func, dfun=None, guess=None):
	def fit_func(data, p0, x=None, weight=None, **kwargs):
		residual, Dresidual = make_residual(func, data, weight=weight, Dfun=dfun, x=x)
		result = leastsq(residual, p0, Dfun=Dresidual, col_deriv=1, **kwargs)
		# result = leastsq(residual, p0, full_output=full_output)
		if kwargs.pop('full_output', False):
			return result
		else:
			p, ier = result
			if ier not in [1, 2, 3, 4]:
				print('Solution not Found')
			return p

	if guess is None:
		return fit_func

	def fit_func_p0(data, p0=None, **kwargs):
		if p0 is None:
			p0 = guess(data)
		return fit_func(data, p0, **kwargs)

	return fit_func_p0

def make_generate(func, p0, size=[100, 100]):
	def generate(p0=p0, size=size, rand=0.0, x=None):
		p = p0 * (1 + 2 * rand * (np.random.rand(len(p0)) - 0.5))
		if x is None:
			x = np.mgrid[[slice(s) for s in size]]
		f = func(x, *p)
		return np.array(p), f
	return generate

class FitResult(OrderedDict):
	def __str__(self):
		return '\n' + '\n'.join(['%20s = %.4g' % (k, v) for k, v in self.items()])

def fit_result_wrap(func, p):
	return FitResult(zip(inspect.getfullargspec(func)[0][1:], p))

def add_noise(img, ampl=0.05, noisetype='random', fringeargs=None):
	"""Noise is added to an image.

	**Inputs**

	  * img: 2d array, containing image data
	  * ampl: float, amplitude of the noise
	  * noisetype: string, value can be one of

		* 'random', adds unbiased white noise
		* 'linear_x', adds a linear gradient along x from 0 to ampl
		* 'linear_y', adds a linear gradient along y from 0 to ampl
		* 'fringes', adds fringes with parameters fringeargs

	  * fringeargs: sequence, containing four values

		* angle: float, angle of fringes in radians with respect to the x-axis
		* freq: float, frequency of the fringes in pixels^{-1}
		* pos: tuple, central position of the fringes with respect to the CoM
		* size: float, size of the Gaussian envelope of the fringes

	**Outputs**

	  * img: 2d array, the input image with noise added to it

	"""

	noisetypes = ['random', 'linear_x', 'linear_y', 'fringes']
	if not noisetype in noisetypes:
		raise ValueError("""noisetype is one of: %s"""%noisetypes)

	if noisetype=='random':
		img = img + (np.random.random_sample(img.shape)-0.5)*ampl

	elif noisetype=='linear_x':
		noise = np.ones(img.shape).transpose()*np.arange(img.shape[0])\
			  /img.shape[0]*ampl
		img = img + noise.transpose()

	elif noisetype=='linear_y':
		noise = np.ones(img.shape)*np.arange(img.shape[1])/img.shape[1]*ampl
		img = img + noise

	elif noisetype=='fringes':
		if not len(fringeargs)==4:
			print("fringeargs needs to contain four values: angle, freq, pos, size")
		angle, freq, pos, size = fringeargs
		xx, yy = np.mgrid[0:img.shape[0], 0:img.shape[1]]

		# center of mass coordinates
		odimg = trans2od(img)
		com = center_of_mass(odimg)
		xx0 = xx - com[0] - pos[0]
		yy0 = yy - com[1] - pos[1]
		yy0 = np.where(yy0==0, 1e-6, yy0)
		rr = np.sqrt(xx0**2 + yy0**2)

		# coordinate projection along fringe axis
		rangle = np.arctan(xx0.astype(float)/yy0)
		rangle = np.where(yy0>0, rangle, rangle + np.pi)
		rfringe = rr*np.cos(angle - rangle)

		noise = fitfuncs.gaussian(rr, ampl, size) * np.sin(2*np.pi*rfringe*freq)
		img = img + noise

	return img