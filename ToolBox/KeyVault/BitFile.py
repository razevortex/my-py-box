from bitarray import bitarray as ba
from bitarray.util import int2ba, ba2int
from os import path as Path


class BitString(ba):
	@classmethod
	def i2b(cls, *val, _N=8):
		v = max(val)
		i = 1
		while v > 2 ** (_N*i):
			i += 1
		temp = [int2ba(v, _N * i) for v in val]
		for byte in temp[1:]:
			temp[0] += byte
		return cls(temp[0])
	
	@classmethod
	def read(cls, file_path:Path):
		temp = cls()
		with open(file_path, 'rb') as f:
			temp.fromfile(f)
		return temp
		
	def write(self, file_path:Path):
		with open(file_path, 'wb') as f:
			self.tofile(f)
	
	def b2i(self, _N=8):
		if _N is None:
			return ba2int(self)
		temp = self[:]
		arr = []
		for i in range(len(temp)//_N):
			arr.append(ba2int(temp[i*_N:(i+1)*_N]))
		return arr


if __name__ == '__main__':
	test = BitString.i2b(*[255, 127, 63, 31])
	test.write(Path('test'))
	test = BitString.read(Path('test'))
	print(test.b2i(_N=8))
