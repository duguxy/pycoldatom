from ...functions.fitclassical import fit_gaussian_node
from .funcNode import nodeFuncWrapper

FitGaussianNode = nodeFuncWrapper(fit_gaussian_node, 
	nodename='FitGaussian', paths=[('Analysis',)],
	outterm=['result', 'err'], cpuheavy=True)

nodelist = [FitGaussianNode]