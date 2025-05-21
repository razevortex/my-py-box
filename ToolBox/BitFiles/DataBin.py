from bitarray import bitarray as ba
from bitarray.util import int2ba, ba2int
from os import path as Path
from dataclasses import dataclass
from datetime import datetime as dt


class Bits(ba):

	@classmethod
	def i2b(cls, value:int, bits:int):
		return cls(int2ba(value, bits))

	@classmethod
	def bytes2b(cls, _bytes:bytes):
		return super(cls).frombytes(_bytes)

	def replace(self, pos:int, value:ba):
		self[:] = self[:pos] + value + self[pos+len(value):]

	def _cut(self, bits:int):
		self[:], temp = self[bits:], self[:bits]
		return temp

	def __lshift__(self, bits:int):
		self[:], temp = self[bits:], self[:bits]
		return temp

	def b2i(self, bits=0):
		return ba2int(self) if bits == 0 else ba2int(self._cut(bits))

	def b2bytes(self) -> bytes:
		return super().tobytes()


class _Type_Int:
	__slots__ = '_type', 'value_', '_range', '_default'
	def __new__(cls, min_:int, max_:int, default=None):
		cls._default = default
		cls._type = int
		cls._range = min_, max_
		return super().__new__(cls)

	def __init__(self, *args):
		self.value_ = self._default

	@property
	def n_bit(self):
		i = 0
		while 2**i < self._range[1] - self._range[0]:
			i += 1
		return i

	@property
	def value(self):
		return self.value_

	@value.setter
	def value(self, value):
		if isinstance(value, self._type) and self._range[0] <= value < self._range[1]:
			self.value_ = value
		if isinstance(value, Bits):
			self.value = self._range[0] + (value << self.n_bit).b2i()

	@property
	def bits(self):
		assert self.value is not None, 'Value wasn`t set yet'
		return Bits.i2b(self.value + abs(self._range[0]), self.n_bit)

	def __repr__(self):
		return f'{self.value}'


class _Type_Float:
	__slots__ = '_type', 'value_', '_range', '_default'
	def __new__(cls, min_:int, max_:int, dec_:int, default=None):
		cls._default = default
		cls._type = float
		cls._range = min_, max_, dec_
		return super().__new__(cls)

	def __init__(self, *args):
		self.value_ = self._default

	@property
	def n_bit(self):
		i = 0
		while 2**i < (self._range[1] - self._range[0]) * 10 ** self._range[2]:
			i += 1
		return i

	@property
	def value(self):
		return self.value_

	@value.setter
	def value(self, value):
		if isinstance(value, self._type) and self._range[0] <= value < self._range[1]:
			self.value_ = round(value, self._range[2])
		if isinstance(value, Bits):
			self.value = round((self._range[0] + (value << self.n_bit).b2i()) * 10 ** -self._range[2], self._range[2])

	@property
	def bits(self):
		assert self.value is not None, 'Value wasn`t set yet'
		return Bits.i2b(int(self.value * 10 ** self._range[2] + abs(self._range[0])), self.n_bit)

	def __repr__(self):
		return f'{self.value}'


class _Type_Bool:
	__slots__ = '_type', 'value_', '_default'
	def __new__(cls, default=None):
		cls._default = default
		cls._type = bool
		return super().__new__(cls)

	def __init__(self, *args):
		self.value_ = self._default

	@property
	def n_bit(self):
		return 1

	@property
	def value(self):
		return self.value_

	@value.setter
	def value(self, value):
		if isinstance(value, self._type):
			self.value_ = value
		if isinstance(value, Bits):
			value = value << self.n_bit
			self.value = bool(value.b2i())

	@property
	def bits(self):
		assert self.value is not None, 'Value wasn`t set yet'
		return Bits.i2b(int(self.value), self.n_bit)

	def __repr__(self):
		return f'{self.value}'


class _Type_String:
	__slots__ = '_type', 'value_', '_charset', '_chars', '_default'
	def __new__(cls, charset:str, chars:int, default=None):
		cls._default = default
		cls._charset = cls._get_dict(charset)
		cls._chars = chars
		cls._type = str
		return super().__new__(cls)

	def __init__(self, *args):
		self.value_ = self._default

	@staticmethod
	def _get_dict(charset):
		i = 0
		while 2 ** i < len(charset) + 1:
			i += 1
		temp = {charset[j]: Bits.i2b(j, i) for j in range(1, len(charset))}
		temp['§PAD'] = Bits.i2b(0, i)
		return temp

	@property
	def n_bit(self):
		return len(self._charset[list(self._charset.keys())[0]]) * self._chars

	@property
	def value(self):
		
		return self.value_

	@value.setter
	def value(self, value):
		if isinstance(value, self._type) and len(value) <= self._chars:
			if all([char in self._charset.keys() for char in value]):
				self.value_ = value
		if isinstance(value, Bits):
			value = value << self.n_bit
			self.value = ''.join(value.decode(self._charset)).replace('§PAD', '')


	@property
	def bits(self):
		assert self.value is not None, 'Value wasn`t set yet'
		temp = Bits('')
		temp.encode(self._charset, self.value)
		while len(temp) < self.n_bit:
			temp += self._charset['NONE']
		return temp

	def __repr__(self):
		return f'{self.value}'
		


class _Type_Datetime:
	__slots__ = '_type', 'value_', '_data', '_format', '_default'
	def __new__(cls, data, format, default=None):
		cls._default = default
		cls._type = dt
		cls._data = data
		cls._format = format
		return super().__new__(cls)

	def __init__(self, *args):
		self.value_ = self._default

	@property
	def data_dict(self):
		return {'day': 6, 'month': 4, 'year': 12, 'hour': 6, 'minute': 6, 'second': 6}

	@property
	def n_bit(self):

		return sum([self.data_dict.get(item, 0) for item in self._data])

	@property
	def value(self):
		return self.value_

	@value.setter
	def value(self, value):
		if isinstance(value, self._type):
			self.value_ = value
		if isinstance(value, Bits):
			value = value << self.n_bit
			temp = {}
			self.value = dt(**{key: value.b2i(self.data_dict.get(key)) for key in self._data})

	@property
	def bits(self):
		assert self.value is not None, 'Value wasn`t set yet'
		temp = Bits('')
		for key in self._data:
			temp += Bits.i2b(getattr(self.value, key), self.data_dict.get(key))
		return temp

	def __repr__(self):
		assert self.value is not None, 'Value wasn`t set yet'
		return f'{self.value.strftime(self._format)}'

