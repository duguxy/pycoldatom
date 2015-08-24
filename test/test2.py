import numpy as np
import cProfile

a = np.random.rand(10000)

def foo(x):
	x = x**2
	return x

def bar(x):
	return x**2

cProfile.run('foo(a)')
cProfile.run('bar(a)') 