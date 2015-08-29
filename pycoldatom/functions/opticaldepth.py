import numpy as np

def calculateOD(sig, ref, bkg):
	od = -np.log((sig-bkg) / (ref-bkg))
	bad = np.logical_or(np.isinf(od), np.isnan(od))
	od[bad] = 0.0
	return od