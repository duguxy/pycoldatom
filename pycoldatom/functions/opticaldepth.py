import numpy as np

def calculateOD(sig, ref, bkg):
	min_step = 1
	sig = sig - bkg
	ref = ref - bkg
	mask = np.logical_or(sig<=0, ref<=0)
	sig = np.maximum(sig, min_step)
	ref = np.maximum(ref, min_step)
	od = -np.log(sig/ref)
	od_0 = np.copy(od)
	od_0[mask] = 0
	return od, od_0