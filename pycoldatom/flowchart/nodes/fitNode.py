from ...functions.fitclassical import fit_gaussian_result
from ...functions.fitbosons import fit_bose_bimodal_result
from .funcNode import nodeFuncWrapper

FitGaussianNode = nodeFuncWrapper(fit_gaussian_result, 
	nodename='FitGaussian', paths=[('Analysis',)],
	outterm=['result', 'err'], cpuheavy=True)

FitBoseBimodalNode = nodeFuncWrapper(fit_bose_bimodal_result,
	nodename='FitBoseBimodal', paths=[('Analysis',)],
	outterm=['result', 'err'], cpuheavy=True)

def fit_gaussian_result_extended(data):
	"""Besides fit result, the data and fit along x0 and y0 are provided"""

	result, err = fit_gaussian_result(data)
	fit = err + data
	x0 = int(result['x0'])
	y0 = int(result['y0'])
	try:
		data_x0 = data[x0, :]
		fit_x0 = fit[x0, :]
		data_y0 = data[:, y0]
		fit_y0 = fit[:, y0]
	except IndexError:
		data_x0 = None
		fit_x0 = None
		data_y0 = None
		fit_y0 = None
	return result, err, data_x0, fit_x0, data_y0, fit_y0

FitGaussianExNode = nodeFuncWrapper(fit_gaussian_result_extended,
	nodename='FitGaussianEx', paths=[('Analysis',)],
	outterm=['result', 'err', 'data_x0', 'fit_x0', 'data_y0', 'fit_y0'],
	cpuheavy=True)

def fit_bose_bimodal_result_extended(data):
	"""Besides fit result, the data and fit along x0 and y0 are provided"""
	
	result, err = fit_bose_bimodal_result(data)
	fit = err + data
	x0 = int(result['x0'])
	y0 = int(result['y0'])
	try:
		data_x0 = data[x0, :]
		fit_x0 = fit[x0, :]
		data_y0 = data[:, y0]
		fit_y0 = fit[:, y0]
	except IndexError:
		data_x0 = None
		fit_x0 = None
		data_y0 = None
		fit_y0 = None
	return result, err, data_x0, fit_x0, data_y0, fit_y0

FitBoseBimodalExNode = nodeFuncWrapper(fit_bose_bimodal_result_extended,
	nodename='FitBoseBimodalEx', paths=[('Analysis',)],
	outterm=['result', 'err', 'data_x0', 'fit_x0', 'data_y0', 'fit_y0'],
	cpuheavy=True)

nodelist = [FitGaussianNode, FitBoseBimodalNode, FitGaussianExNode, FitBoseBimodalExNode]