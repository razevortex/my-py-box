class DecimalUnits(object):
	__slots__ = 'units'

	def __init__(self):
		self.units = (('p', 'pico'), ('n', 'nano'), ('u', 'micro'), ('m', 'milli'), ('', None),
					  ('k', 'kilo'), ('M', 'mega'), ('G', 'giga'), ('t', 'tetra'))

	def _distance(self, this=None, to=None):
	  return self._get_index(this) - self._get_index(to)

	def _get_index(self, this):
	  for i, unit in enumerate(self.units):
		  if this in unit:
			  return i

	def _convert(self, value, this:str, to:str):
		return value * (10 ** (self._distance(this, to) * 3))

	def convert(self, value, unit, cutoff='.3f'):
		i = self._get_index(unit)
		while value > 1000 or value < 1:
			if value < 1:
				i, value = i - 1, value * (10 ** 3)
			elif value > 1000:
				i, value = i + 1, value * (10 ** -3)
		return float(f'{value:{cutoff}}'), self.units[i][1]

	def base(self, value, unit):
		return self._convert(value, unit, '')

class Time2Clock(object):
	'''
	Time2Clock is a converter for a Time value ( of any unit ) to a readable hh:mm:ss.xxx.xxx.xxx string
	'''
	__slots__ = 'units', 'decimal_pos'
	sub = DecimalUnits()
	
	def __init__(self, decimal_pos:bool | int = True) -> None:
		self.units = (('h', 'hour'), ('m', 'minute'), ('s', 'seconds'))
		self.decimal_pos = decimal_pos

	def _distance(self, this='', to=''):
		return self._get_index(this) - self._get_index(to)

	def _get_index(self, this):
		for i, unit in enumerate(self.units):
			if this in unit:
				return i
		return False

	@staticmethod
	def _calc(value, dist):
		temp = 60 ** abs(dist)
		if dist == 0:
			return value, value
		elif dist < 0:
			return value * temp, 0
		else:
			return value // temp, value - (value // temp * temp)

	def _base(self, value, unit):
		return self.sub.base(value, unit)

	def _stringify(self, arr:list):
		if '.' in str(arr[2]):
			temp = str(arr[2]).split('.')
		else:
			temp = str(arr[2]), '0'
		arr[2] = temp[0]
		arr = [f'{a}' if len(str(a)) == 2 else f'0{a}' for a in arr]
		string = f'{arr[0]}:{arr[1]}:{arr[2]}'
		if self.decimal_pos is not False:
			if type(self.decimal_pos) != bool:
				decimal = f'{temp[1]}{"0" * 9}'[:self.decimal_pos]
			else:
				decimal = f'{temp[1]}{"0" * 9}'[:9]
			temp = '.'
			for i, d in enumerate(decimal):
				temp += d
				if (i+1) % 3 == 0:
					temp += '.'
			return string + temp[:-1]
		else:
			return string

	def form(self, value, unit):
		if not self._get_index(unit):
			value, unit = self._base(value, unit), 's'
		if unit != 's':
			value, _ = self._calc(value, self._distance(unit, 's'))
		arr = []
		for u in self.units:
			u_val, value = self._calc(value, self._distance('s', u[0]))
			if u[0] != 's':
				arr.append(int(u_val))
			else:
				arr.append(u_val)
		return self._stringify(arr)

	def past_time(self, start, end, default_unit='n'):
		'''
		calculates the time diff and returns the form string
		:param start: tuple(value:int, unit:str)|value:int
		:param end: tuple(value:int, unit:str)|value:int
		:return: str
		'''
		start, end = (val if type(val) == tuple else (val, default_unit) for val in [start, end])
		return self.form(self._base(*end) - self._base(*start), 's')
	
	
if __name__ == '__main__':
	test = Time2Clock(False)
	print(test.form(100, 's'))
		
		
		