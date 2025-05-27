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


class _Type:
	__slots__ = '_type', 'value_', '_default'

	def __new__(cls, default=None):
		cls._default = default
		return super().__new__(cls)

	def __init__(self, *args):
		self.value_ = self._default

	@property
	def value(self):
		return self.value_

	def __repr__(self):
		return f'{self.value}'


class _Int(_Type):
	__slots__ = '_type', 'value_', '_range', '_default'
	def __new__(cls, min_:int, max_:int, default=None):
		cls._default = default
		cls._type = int
		cls._range = min_, max_
		return super().__new__(cls)

	@classmethod
	def build(cls, min_:int, max_:int, default=None):
		class new(_Int):
			__name__ = f'_Int_{min_}_{max}'
			def __new__(cls, *args, **kwargs):
				return super().__new__(*args, **kwargs)

		return new(min_, max_, default=default)

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


class _Float(_Type):
	__slots__ = '_type', 'value_', '_range', '_default'
	def __new__(cls, min_:int, max_:int, dec_:int, default=None):
		cls._default = default
		cls._type = float
		cls._range = min_, max_, dec_
		return super().__new__(cls)
		
	@classmethod
	def build(cls, min_:int, max_:int, dec_:int, default=None):
		class new(cls):
			_default = default
			_type = int
			_range = min_, max_, dec_
			__name__ = f'_Float_{min_}_{max}_{dec_}'
			def __new__(cls, *args, **kwargs):
				return cls.__new__()
			def __init__(self, value:float):
				self.value_ = value
		return new
		
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


class _Bool(_Type):
	__slots__ = '_type', 'value_', '_default'
	def __new__(cls, default=None):
		cls._default = default
		cls._type = bool
		return super().__new__(cls)

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


class _String(_Type):
	__slots__ = '_type', 'value_', '_charset', '_chars', '_default'
	def __new__(cls, charset:str, chars:int, default=None):
		cls._default = default
		cls._charset = cls._get_dict(charset)
		cls._chars = chars
		cls._type = str

	@classmethod
	def build(cls, charset:str, chars:int, default=None):
		class new(cls):
			_default = default
			_charset = cls._get_dict(charset)
			_chars = chars
			_type = str
			__name__ = f'_Int_{min_}_{max}'
			def __new__(cls, *args, **kwargs):
				return cls.__new__()
				
			def __init__(self, value:str):
				self.value_ = value
		return new
	@staticmethod
	def _get_dict(charset):
		i = 0
		while 2 ** i < len(charset) + 1:
			i += 1
		temp = {charset[j]: Bits.i2b(j+1, i) for j in range(len(charset))}
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
			if all([char in list(self._charset.keys()) for char in value]):
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
			temp += self._charset['§PAD']
		return temp


class _Datetime(_Type):
	__slots__ = '_type', 'value_', '_data', '_format', '_default'
	def __new__(cls, data, format, default=None):
		cls._default = default
		cls._type = dt
		cls._data = data
		cls._format = format
		return super().__new__(cls)

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

class DataObject:
	__slots__ = ()
	_type_map = {}

	def __init__(self, *args):
		for i, slot in enumerate(self.__slots__):
			super().__setattr__(slot, self._type_map.get(slot))

	@classmethod
	def build(cls, **kwargs):
		class new(DataObject):
			__slots__ = tuple(kwargs.keys())
			_type_map = kwargs
		return new
		
	@classmethod
	def set_values(cls, **kwargs):
		cls = cls()
		for key, value in kwargs.items():
			if key in cls.__slots__:
				cls._type_map.get(key).value = value
		return cls
	
	@classmethod
	def from_bits(cls, bits:Bits):
		cls = cls()
		for slot in cls.__slots__:
			cls.__setattr__(slot, bits)
		return cls
								
	def __getattribute__(self, key):
		if isinstance(super().__getattribute__(key), _Type):
			return super().__getattribute__(key).value
		else:
			return super().__getattribute__(key)

	def __setattr__(self, key, value):
		if isinstance(value, _Type):
			super().__setattr__(key, value)
		elif isinstance(super().__getattribute__(key), _Type):
			super().__getattribute__(key).value = value
		else:
			super().__setattr__(key, value)

	@property
	def bits(self):
		temp = Bits('')
		for slot in self.__slots__:
			temp += super().__getattribute__(slot).bits
		return temp

	def __repr__(self):
		return '\n'.join([f'{self.__getattribute__(slot)}' for slot in self.__slots__])

	def __tuple__(self):
		return tuple([self.__getattribute__(slot) for slot in self.__slots__])


if __name__ == '__main__':
	aObj = DataObject.build(**{'a': _Int(0, 255), 'b': _Float(0, 1, 5)})
	temp = aObj.set_values(a=123, b=0.12345)
	print(temp)
	print(temp.bits)
	temp = aObj.from_bits(test.bits)
	print(temp)
