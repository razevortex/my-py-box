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

class _T:
	__slots__ = '_value_'
	default = None
	type_ = object

	def __init__(self, value=None):
		self._value_ = None
		if not isinstance(value, (self.type_, Bits)):
			self._value_ = self.default
		else:
			self.value = value

	def __repr__(self):
		return f'{self.value}'

	@property
	def value(self):
		return self._value_

	@value.setter
	def value(self, value):
		if isinstance(value, self.type_):
			self._value_ = value


class BinTypes:
	@classmethod
	def _Int(cls, min_:int, max_:int, name='_Int', default_=None):
		class new(_T):
			__name__ = name
			__slots__ = '_value_'
			default = default_
			type_ = int
			range = min_, max_

			def __init__(self, value=None):
				super().__init__(value=value)

			@property
			def value(self):
				return self._value_

			@property
			def n_bit(self):
				i = 0
				while 2**i < self.range[1] - self.range[0]:
					i += 1
				return i

			@value.setter
			def value(self, value):
				if isinstance(value, self.type_) and self.range[0] <= value < self.range[1]:
					self._value_ = value
				elif isinstance(value, Bits):
					self._value_ = self.range[0] + (value << self.n_bit).b2i()
				else:
					print(f'{value} of type {type(value)} could not be set type {self.type_} or Bits was expectet')
	 
			@property
			def bits(self):
				assert self.value is not None, 'Value wasn`t set yet'
				return Bits.i2b(self.value + abs(self.range[0]), self.n_bit)

			def __repr__(self):
				return f'{self.value}'

		return new

	@classmethod
	def _Float(cls, min_:int, max_:int, dec_:int, name='_Float', default_=None):
		class new(_T):
			__name__ = name
			__slots__ = '_value_'
			default = default_
			type_ = float
			range = min_, max_, dec_

			def __init__(self, value=None):
				super().__init__(value=value)

			@property
			def value(self):
				return self._value_

			@property
			def n_bit(self):
				i = 0
				while 2**i < (self.range[1] - self.range[0]):# * 10 ** self.range[2]:
					i += 1
				return i + (self.range[2] * 4)

			@value.setter
			def value(self, value):
				if isinstance(value, self.type_) and self.range[0] <= value < self.range[1]:
					self._value_ = round(value, self.range[2])
				elif isinstance(value, Bits):
					temp = f'{self.range[0] + (value << (self.n_bit - self.range[2] * 4)).b2i()}.'
					for _ in range(self.range[2]):
						temp += f'{(value << 4).b2i()}'
					self._value_ = float(temp.rstrip('0'))
				else:
					print(f'{value} of type {type(value)} could not be set type {self.type_} or Bits was expectet')

			@property
			def bits(self):
				assert self.value is not None, 'Value wasn`t set yet'
				temp = Bits.i2b(int(self.value) - self.range[0], self.n_bit - self.range[2] * 4)
				for char in str(self.value).split('.')[1][:self.range[2]+1]:
					temp[:] = temp[:] + Bits.i2b(int(char), 4)[:]
				while len(temp) < self.n_bit:
					temp[:] = temp[:] + Bits.i2b(0, 4)[:]
				return temp

			def __repr__(self):
				return f'{self.value}'

		return new


	@classmethod
	def _Bool(cls, name='_Bool', default_=None):
		class new(_T):
			__name__ = name
			__slots__ = '_value_'
			default = default_
			type_ = bool

			def __init__(self, value=None):
				super().__init__(value=value)

			@property
			def value(self):
				return self._value_

			@value.setter
			def value(self, value):
				if isinstance(value, self.type_):
					self._value_ = value
				elif isinstance(value, Bits):
					self._value_ = (value << self.n_bit).b2i() == 1
				else:
					print(f'{value} of type {type(value)} could not be set type {self.type_} or Bits was expectet')
	 
			@property
			def n_bit(self):
				return 1

			@property
			def bits(self):
				assert self.value is not None, 'Value wasn`t set yet'
				return Bits.i2b(int(self.value), self.n_bit)

			def __repr__(self):
				return f'{self.value}'

		return new

	@classmethod
	def _String(cls, charset_:str, chars_:int, default_=None, name='_String'):

		def _get_dict(charset):
			i = 0
			while 2 ** i < len(charset) + 1:
				i += 1
			temp = {charset[j]: Bits.i2b(j+1, i) for j in range(len(charset))}
			temp['§PAD'] = Bits.i2b(0, i)
			return temp

		class new(_T):
			__name__ = name
			__slots__ = '_value_'
			default = default_
			type_ = str
			charset = _get_dict(charset_)
			chars = chars_

			def __init__(self, value=None):
				super().__init__(value=value)

			@property
			def n_bit(self):
				return len(self.charset[list(self.charset.keys())[0]]) * self.chars

			@property
			def value(self):
				return self._value_

			@value.setter
			def value(self, value):
				if isinstance(value, self.type_) and len(value) <= self.chars:
					if all([char in list(self.charset.keys()) for char in value]):
						self._value_ = value
				elif isinstance(value, Bits):
					value = value << self.n_bit
					self._value_ = ''.join(value.decode(self.charset)).replace('§PAD', '')
				else:
					print(f'{value} of type {type(value)} could not be set type {self.type_} or Bits was expectet')
	 
			@property
			def bits(self):
				assert self.value is not None, 'Value wasn`t set yet'
				temp = Bits('')
				temp.encode(self.charset, self.value)
				while len(temp) < self.n_bit:
					temp += self.charset['§PAD']
				return temp

			def __repr__(self):
				return f'{self.value}'

		return new

	@classmethod
	def _Datetime(cls, _data:list, _format:str, default_=None, name='_Datetime'):
		class new(_T):
			__name__ = name
			__slots__ = '_value_'
			default = default_
			type_ = dt
			data = _data
			format = _format

			def __init__(self, value=None):
				super().__init__(value=value)

			@property
			def data_dict(self):
				return {'day': 6, 'month': 4, 'year': 12, 'hour': 6, 'minute': 6, 'second': 6}

			@property
			def n_bit(self):
				return sum([self.data_dict.get(item, 0) for item in self.data])

			@property
			def value(self):
				return self._value_

			@value.setter
			def value(self, value):
				if isinstance(value, self.type_):
					self._value_ = value
				elif isinstance(value, Bits):
					value = value << self.n_bit
					temp = {}
					self.value = dt(**{key: 1 if key not in self.data else value.b2i(val) for key, val in self.data_dict.items()})
				else:
					print(f'{value} of type {type(value)} could not be set type {self.type_} or Bits was expectet')
		
			@property
			def bits(self):
				assert self.value is not None, 'Value wasn`t set yet'
				temp = Bits('')
				for key in self.data:
					temp += Bits.i2b(getattr(self.value, key), self.data_dict.get(key, 0))
				return temp

			def __repr__(self):
				assert self.value is not None, 'Value wasn`t set yet'
				return f'{self.value.strftime(self.format)}'
		
		return new



def databin_basic_test():
	def sep(_type):
		print(f'\n-\t-\t-\t-\t-\n\n\t{_type} :\n')
	sep('Int')
	for i, item in enumerate([BinTypes._Int(0, 100), BinTypes._Int(-100, 0)]):
		temp = item([50, -50][i])
		print(f'value => {temp}')
		temp.value = temp.value + 10
		print(f'value + 10 => {temp}')
		print(f'bits => {temp.bits}')
		temp.value = temp.bits
		print(f'set with bits => {temp}')
	sep('Float')
	for i, item in enumerate([BinTypes._Float(0, 100, 2), BinTypes._Float(-100, 0, 2)]):
		temp = item([50/2, -50/2][i])
		print(f'value => {temp}')
		temp.value = temp.value + 0.05
		print(f'value + 0.05 => {temp}')
		print(f'bits => {temp.bits}')
		temp.value = temp.bits
		print(f'set with bits => {temp}')
	sep('Bool')
	temp = BinTypes._Bool()
	temp = temp(False)
	print(f'value => {temp}')
	print(f'bits => {temp.bits}')
	temp.value = temp.bits
	print(f'set with bits => {temp}')
	sep('String')
	temp = BinTypes._String("abcd HeloWr!",  32)
	temp = temp('Hello World!')
	print(f'value => {temp}')
	print(f'bits => {temp.bits}')
	temp.value = temp.bits
	print(f'set with bits => {temp}')
	sep('Datetime')
	temp = BinTypes._Datetime(['hour', 'minute', 'second'], '%H:%M:%S')
	temp = temp(dt.now())
	print(f'value => {temp}')
	print(f'bits => {temp.bits}')
	temp.value = temp.bits
	print(f'set with bits => {temp}')
