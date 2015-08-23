from ...functions.fitclassical import fit_gaussian_result
from .funcNode import nodeFuncWrapper

FitGaussianNode = nodeFuncWrapper(fit_gaussian_result, 
	nodename='FitGaussian', paths=[('Analysis',)],
	outterm=['result', 'err'], cpuheavy=True)

nodelist = [FitGaussianNode]