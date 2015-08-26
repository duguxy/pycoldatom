from pyclibrary.c_parser import Type
import pickle

class A(tuple):
	def __repr__(self):
		return ','.join(map(repr, self))

a=Type('type_spec')
print(a)
c=A((1,2))
with open('type.dump', 'wb') as f:
	pickle.dump([a, c], f)
with open('type.dump', 'rb') as f:
	b, d = pickle.load(f)
print(b)
print(b[0])