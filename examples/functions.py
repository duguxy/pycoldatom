from init_flowchart import *

from pycoldatom.functions.fitclassical import generate_gaussian, fit_gaussian, guess_gaussian

def test_gaussian():
	p, data = generate_gaussian()
	p0 = guess_gaussian(data)
	p1 = fit_gaussian(data, p0)
	print('p:', p)
	print('p0:', p0)
	print('p1:', p1)

test_gaussian()
