from ...functions.fitclassical import fit_gaussian_result
from ...functions.fitbosons import fit_bose_bimodal_result
from .funcNode import nodeFuncWrapper

FitGaussianNode = nodeFuncWrapper(fit_gaussian_result, 
	nodename='FitGaussian', paths=[('Analysis',)],
	outterm=['result', 'err'], cpuheavy=True)

FitBoseBimodalNode = nodeFuncWrapper(fit_bose_bimodal_result,
	nodename='FitBoseBimodal', paths=[('Analysis',)],
	outterm=['result', 'err'], cpuheavy=True)

nodelist = [FitGaussianNode, FitBoseBimodalNode]