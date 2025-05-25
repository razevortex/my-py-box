from SlotObjects.MathSlotClass import MathObj
from ToolBox.BitFiles.DataBin import _Type, _Int, _Float, _String, _Bool, _Datetime, DataObject, Bits
from random import randint as rng
from time import time

class _Color(MathObj):
	__slots__ = ()
	_store_obj = DataObject.build(**{slot: _Int(0, 256) for slot in __slots__})

	def __init__(self, *args):
		super().__init__(*args)

	def __dict__(self):
		return {slot: self.__getattribute__(slot) for slot in self.__slots__}

	@property
	def bits(self):
		return self._store_obj.set_values(**self.__dict__()).bits

	@classmethod
	def from_bits(cls, bits:Bits):
		temp = cls._store_obj.from_bits(bits)
		return cls(*temp.__tuple__())

	@classmethod
	def random(cls):
		return cls(*[rng(0, 256) for _ in range(len(cls.__slots__))])

class Greyscale(_Color):
	__slots__ = 'h'
	_store_obj = DataObject.build(**{slot: _Int(0, 256) for slot in __slots__})
	def __init__(self, *args):
		super().__init__(*args)

	@classmethod
	def convert(cls, color):
		temp = [color.__getattribute__(slot) for slot in color.__slots__ if slot != 'a']
		temp = 0 if sum(temp) == 0 else sum(temp) // len(temp)
		if 'a' in color.__slots__:
			temp = 0 if color.a == 0 else color.a / 255 * temp
		return cls(temp)

class RGB(_Color):
	__slots__ = 'r', 'g', 'b'
	_store_obj = DataObject.build(**{slot: _Int(0, 256) for slot in __slots__})
	def __init__(self, *args):
		super().__init__(*args)

	@classmethod
	def convert(cls, color):
		if 'h' in color.__slots__:
			return cls(*[color.h for _ in range(3)])
		elif 'a' in color.__slots__:
			a = 0 if color.a == 0 else color.a / 255
			return cls(*[color.__getattribute__(slot) * a for slot in color.__slots__ if slot != 'a'])

	@property
	def h(self):
		return 0 if sum(self.__tuple__()) == 0 else sum(self.__tuple__()) // len(self.__tuple__())

class RGBA(_Color):
	__slots__ = 'r', 'g', 'b', 'a'
	_store_obj = DataObject.build(**{slot: _Int(0, 256) for slot in __slots__})
	def __init__(self, *args):
		super().__init__(*args)

	@classmethod
	def convert(cls, color, a=255):
		if 'h' in color.__slots__:
			return cls(*[color.h for _ in range(3)])
		return cls(*[c for c in color.__tuple__()] + [a,])
	
	@property
	def alpha(self):
		return 0 if self.a == 0 else self.a / 255

	def add_alpha_to(self, color):
		temp = 0
		for slot in self.__slots__:
			if slot != 'a':
				temp += abs(self.__getattribute__(slot) - color.__getattribute__(slot)) * (1 / 255)
		temp *= (1 / 3)
		return self.__class__.convert(color, a=int(abs(255*temp-self.a)))

	def apply_on_bg(self, bg):
		return bg + (RGB(self.r, self.g, self.b) - bg) * self.alpha

	@property
	def h(self):
		return 0 if sum(self.__tuple__()) == 0 else sum(self.__tuple__()) // len(self.__tuple__())


def test(t=1):
	test = RGB(128, 128, 128)
	test2 = RGBA(128, 0, 255, 128)
	print(RGB.convert(test2))
	print(test.bits, test2.bits)
	print(test2.apply_on_bg(test))
	a, b = RGBA(0, 128, 128, 255), RGBA(128, 128, 128, 0)
	print(a.add_alpha_to(test))
	print(b.add_alpha_to(test))
	def bench(t, n=10):
		i = 0
		tmp = RGB(rng(0, 256), rng(0, 256), rng(0, 256)).bits
		for _ in [RGB(rng(0, 256), rng(0, 256), rng(0, 256)).bits for _ in range(n)]:
			tmp += _
		print(f'testsize n={n}')
		start = time()
		while time() - start < t and i < n:
			temp = RGB.from_bits(tmp)
			i += 1
			if not i < n:
				print(f'n reached after {time() - start} increase testsize')
				return bench(t, n=n*10)
		print(f'in t={t} {i} RGB objects read from bits')
	bench(t)
