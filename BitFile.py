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

'''class bit(ba):
    @classmethod
    def readf(cls, file):
        if os.path.exists(file):
            temp = cls()
            with open(file, 'rb') as f:
                temp.fromfile(f)
            return temp[8:-temp[:8].count(1)]
        else:
            return cls()

    def __str__(self):
        i = 0
        temp = ''
        while i < len(self):
            temp += '[' + ''.join([str(t) for t in self[i:i+8]]) + '] '
            i += 8
        return temp

    def cut(self, bits:int):
        temp, self[:] = self[:bits], self[bits:]
        return temp

    def _pad(self):
        i = 0
        pad = [[0 for _ in range(8)], []]
        while (len(self) + i) % 8 != 0:
            pad[0][i] = 1
            pad[1].append(0)
            i += 1
        return bit(pad[0]) + self + bit(pad[1])

    def writef(self, file):
        temp = self if len(self) % 8 == 0 else self._pad()
        with open(file, 'wb') as f:
            temp.tofile(f)

    def rng_array(self,  size:int, chance:tuple):
        self.size = size
        return bit([int(rng(0, chance[1]) > chance[0]) for i in range(size)])


def i2b(val:int, len:int):
    return bit(int2ba(val, len))

def b2i(bits:bit):
    return ba2int(bits)'''
if __name__ == '__main__':
	test = BitString.i2b(*[255, 127, 63, 31])
	test.write(Path('test'))
	test = BitString.read(Path('test'))
	print(test.b2i(_N=8))
