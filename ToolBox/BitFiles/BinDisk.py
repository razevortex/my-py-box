from bitarray import bitarray as ba
from bitarray.util import int2ba as i2b, ba2int as b2i


class Hex(ba):
	chars = '0123456789ABCDEF'

	@classmethod
	def make(cls, value):
		if isinstance(value, int):
			assert 0 <= value < 16, f'value of type(int) {value} must be >= 0 and < 16'
			return cls(i2b(value, 4))
		if isinstance(value, ba):
			assert len(value) == 4, f'value of type(ba) must be len 4 but is {len(value)}'
			return cls('') + value
		if isinstance(value, str):
			assert value in cls.chars, f'value of type(str) must be in {cls.chars} but is {value}'
			return cls(i2b(cls.chars.index(value)))

	@staticmethod
	def cout(bin, groups_size=2, row_groups=16, seperator=' '):
		string = ''
		for i, char in enumerate([f'{Hex.make(bin[i:i+4])}' for i in range(0, len(bin), 4)]):
			if i != 0:
				if i % groups_size == 0:
					string += seperator
				if i % (groups_size * row_groups) == 0:
					string += '\n'
			string += char
		return string
	
	def __int__(self):
		return b2i(self)

	def __str__(self):
		return self.chars[self.__int__()]


class BinSlice:
	__slots__ = '_start', '_stop', 'blocksize'

	def __init__(self, start:int, stop=1, blocksize=8):
		self._start = start
		self._stop = stop
		self.blocksize = blocksize
		
	@property
	def start(self):
		return self._start * self.blocksize
	
	@property
	def stop(self):
		return self.start + self._stop * self.blocksize
	

class Bin(ba):
	@classmethod
	def make(cls, value=''):
		return cls(ba(value))

	@classmethod
	def join(cls, *args, type_=ba, size=None):
		temp = cls('')
		for arg in args:
			temp += arg
	
	def __getitem__(self, i:int|BinSlice):
		if isinstance(i, BinSlice):
			return super().__getitem__(slice(i.start,i.stop, 1))
		else:
			return super().__getitem__(i)
		
	@classmethod
	def h2b(cls, hex):
		temp = cls('')
		if isinstance(hex, str):
			hex = [Hex.make(char) for char in hex if char in Hex.chars]
		if isinstance(hex, Hex):
			hex = [hex,]
		for h in hex:
			temp += h
		return temp
		
	@staticmethod
	def _bit_4_int(integer):
		i = 0
		while 2 ** i < integer:
			i += 1
		return i
	
	@property
	def b2i(self):
		return b2i(self)
	
	@property
	def b2h(self):
		string = ''
		for i in range(0, len(self), 4):
			string += '0123456789ABCDEF'[self[i:i+4].b2i]
		return string
		
	def append_int(self, integer, bits=8):
		bits = bits if not bits is None else self._bit_4_int(integer)
		assert 2 ** bits > integer, f'{integer} doesnt fit into {bits} bits'
		self[:] = self[:] + i2b(integer, bits)[:]

	def __int__(self):
		return b2i(self)
	
class DiskRead(Bin):
	@staticmethod
	def _read_disk(start_byte, n_bytes, disk_id):
		temp = DiskRead('')
		handle = open(r'\\.\PhysicalDrive' + str(disk_id), 'rb')
		handle.seek(start_byte)
		temp.frombytes(handle.read(n_bytes))
		return temp

	def bin2file(self, path):
		with open(path, 'wb') as f:
			f.write(self.tobytes())


class MBR_Struct:
	__slots__ = 'MBR', 'Bootstrap', 'Parts', 'Bootsignature'
	def __init__(self):
		self.MBR = BinSlice(0, 512)
		self.Bootstrap = BinSlice(0, 446)
		self.Parts = (BinSlice(446, 16), BinSlice(462, 16), BinSlice(478, 16), BinSlice(494, 16))
		self.Bootsignature = BinSlice(510, 2)
	
	def cout(self, binary):
		string = f'MasterBootRecord bootsignature{binary[self.Bootsignature].__int__()} doesnt match {Bin("0101010110101010").__int__()}'
		assert binary[self.Bootsignature].__int__() == Bin("0101010110101010").__int__(), string
		
		string = 'MasterBootRecord ->\n\tBootstrap ->\n'
		string += ''.join([f'\t\t{line}\n' for line in Hex.cout(binary[self.Bootstrap]).split('\n')])
		for i, part in enumerate(self.Parts):
			string += f'\tPartition{i} ->\n'
			for line in self._PartStruct.cout(binary[part]):
				string += f'\t\t{line}\n'
		string += f'\tBootsignature ->\n\t\t{Hex.cout(binary[self.Bootsignature])}'
		return string

	@property
	def _PartStruct(self):
		class PartitionStruct:
			__slots__ = 'Status', 'CHS_First', 'Type', 'CHS_Last', 'LBA_First_Sector', 'Number_of_Sectors'
			def __init__(self):
				self.Status = BinSlice(0, 1)
				self.CHS_First = BinSlice(1, 3)
				self.Type = BinSlice(4, 1)
				self.CHS_Last = BinSlice(5, 3)
				self.LBA_First_Sector = BinSlice(8, 4)
				self.Number_of_Sectors = BinSlice(12, 4)
			
			def cout(self, PartitionBlock):
				return [f'\t{slot} -> {Hex.cout(PartitionBlock[self.__getattribute__(slot)])}' for slot in self.__slots__]
		
		return PartitionStruct()
	

# Execution Sandbox
if __name__ == '__main__':
	mbr = MBR_Struct()
	temp = DiskRead._read_disk(0, 512, 5)
	print(mbr.cout(temp))
	#for part in (BinSlice(446, 16), BinSlice(462, 16), BinSlice(478, 16), BinSlice(494, 16)):
	#	print(Hex.cout(temp[part]))
	#print(temp)
	#print(Hex.cout(temp))
	
