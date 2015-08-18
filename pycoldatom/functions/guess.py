import cv2
import numpy as np



def test():
	from refimages import add_noise

	xx, yy = np.mgrid[0:100, 0:100]
	data = 1.5*np.exp(-((xx-60)/40)**2-((yy-40)/15)**2) +2.0
	data = add_noise(data, ampl=0.1)
	guess_gaussian(data)

if __name__ == '__main__':
	test()