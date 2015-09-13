import numpy as np
a=np.random.random((3,3))
b=np.random.random(3)
print(a*b==np.dot(a,np.diag(b)))