from bitarray import bitarray as ba
from bitarray.util import int2ba, ba2int
from os import path as Path


class BitFile(ba):
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
	
	def __str__(self):
		return ''.join([str(val) for val in self])
	
	def view(self, bit_per_block=8, blocks_per_row=8, out=print):
		blocks = [f'[{self[i:i+bit_per_block]}]' for i in range(0, len(self), bit_per_block)]
		string = f'BitFile => {len(self)} bit\n'
		for row in range(max(len(blocks) // blocks_per_row, 1)):
			string += ' '.join(blocks[row:row+blocks_per_row]) + '\n'
		return out(string)
	
	def __lshift__(self, val:int):
		temp, self[:] = self[:val], self[val:len(self)-1]
		return temp
	
	def __rshift__(self, val:int):
		self[:] = self.__class__('0' * val) + self[:len(self)-1]
		return self
	
	def __getitem__(self, i:int|slice):
		if isinstance(i, int):
			return int(super().__getitem__(i))
		elif isinstance(i, slice):
			return self.__class__(super().__getitem__(i))
		
	def __setitem__(self, i:int|slice, value):
		if isinstance(i, slice):
			assert isinstance(value, (str, BitFile)), f'to set a slice of BitFile, the value has to be type(str, BitFile) not {type(value)}'
			value = value if not isinstance(value, str) else BitFile(value)
			i = slice(0 if i.start is None else i.start, len(self) - 1 if i.stop is None else i.stop)
			value = self[: i.start if i.start >= 0 else 0] + value + self[i.stop: None if i.start >= 0 else i.start]
			super().__setitem__(slice(None, None, None), value)
			return self.__class__(value)
		super().__setitem__(i, value)
		
	def write(self, file_path:Path):
		with open(file_path, 'wb') as f:
			self.tofile(f)
	
	def b2i(self, _N:int|None=8):
		if _N is None:
			return ba2int(self)
		temp = self[:]
		arr = []
		for i in range(len(temp)//_N):
			arr.append(ba2int(temp[i*_N:(i+1)*_N]))
		return arr


class Header(BitFile):
	BIT_MAPPING = {'pad': slice(0, 1, 1), 'byte_per_block': slice(1, 8, 1), 'size_in_blocks': slice(8, 40, 1), 'last_block': slice(40, 48, 1)}
	
	def un_byte_pad(self):
		while self[self.BIT_MAPPING['pad']] != BitFile('1'):
			_ = self << 1

	def byte_pad(self):
		while len(self) % 8 != 0:
			self >> 1
	
	@property
	def _get_slice(self):
		return slice(48, 48 + self.block_size_bit * self.blocks + self.last_block * 8, 1)
	
	@classmethod
	def _empty(cls):
		return cls('1') + cls('0' * 47)
	
	def set_header(self, this):
		self.block_size_bit = this
		self.blocks = this
		self.last_block = this
		self[:] = self + this
		self.byte_pad()
		
	@classmethod
	def create_new(cls, this):
		temp = cls._empty()
		temp.set_header(this)
		#temp.block_size_bit = this
		#temp.blocks = this
		#temp.last_block = this
		#temp += this
		return temp

	@classmethod
	def load_files(cls, bin_file, *args):
		temp = cls.read(bin_file)
		data = {}
		for name in args:
			temp.un_byte_pad()
			data[name] = temp[temp._get_slice]
			temp = temp[temp._get_slice.stop:]
		return data

	@property
	def block_size_bit(self):
		return min(self[self.BIT_MAPPING['byte_per_block']].b2i(_N=None) * 8, 8)

	@block_size_bit.setter
	def block_size_bit(self, value):
		n_bytes = len(value) // 8
		for i in range(1, 127):
			if 2 ** 32 * i > n_bytes:
				self[self.BIT_MAPPING['byte_per_block']] = BitFile.i2b(i, _N=7)
				return
				
	@property
	def blocks(self):
		return self[self.BIT_MAPPING['size_in_blocks']].b2i(_N=None)
	
	@blocks.setter
	def blocks(self, value):
		self[self.BIT_MAPPING['size_in_blocks']] = BitFile.i2b(len(value) // self.block_size_bit, _N=32)

	@property
	def last_block(self):
		return self[self.BIT_MAPPING['last_block']].b2i(_N=None)
	
	@last_block.setter
	def last_block(self, value):
		value = (len(value) - self.block_size_bit * self.blocks) // 8
		self[self.BIT_MAPPING['last_block']] = BitFile.i2b(value)
		

if __name__ == '__main__':
	pass