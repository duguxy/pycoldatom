import numpy as np

def calculateOD(sig, ref, bkg):
	min_step = 1
	sig = np.maximum(sig-bkg, min_step)
	ref = np.maximum(ref-bkg, min_step)
	od = -np.log(sig/ref)
	return od