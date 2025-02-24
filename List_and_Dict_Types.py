class StickyList(list):
  '''
  A List type with changes to its + and += behavior it will now always extend itself by adding the other value 
  '''
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def __add__(self, other):
		if type(other) == list or type(other) == tuple:
			return StickyList(self + list(other))
		else:
			return StickyList(self + [other])

	def __iadd__(self, other):
		if type(other) == list or type(other) == tuple:
			self.extend(list(other))
		else:
			self.extend([other])
		return self


class NamedCounter(dict):
  '''
  A Dict type each time NamedCounter +/+= keyword the keys value is raised by 1 also keywords that are missing get created with 0 and then raised by 1
  '''
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def __repr__(self):
		vals = [(val, key) for key, val in self.items()]
		vals.sort()
		msg = ''
		for val in vals:		msg += f'{val[1]} = {val[0]}\n'
		msg += f'\nTOTAL: {sum([v[0] for v in vals])}'
		return msg

	def __copy__(self):
		clone = NamedCounter()
		clone.update(self)
		return clone

	def __add__(self, other):
		for key, val in other.items():
			other[key] = self[key] + val
		self.update(other)
		return self

	def __iadd__(self, other):
		if type(other) == list:
			for key in other:
				self[key] += 1
		elif type(other) == str:
			self[other] += 1
		return self

	def __missing__(self, key):
		self[key] = 0
		return self[key]


class NamedLister(NamedCounter):
  '''
  A Dict Type based on NamedCounter but +/+= with a key: value pair and the keyvalues are a StickyList means the value is a list that is extended with the value 
  '''
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return ''.join([f'{key}: {val}\n' for key, val in self.items()])

	def __missing__(self, key):
		self[key] = StickyList()
		return self[key]

	def __iadd__(self, other:dict):
		if type(other) == dict:
			for key, val in other.items():
				self[key] += val
			return self
		arr = [] + [other] if type(other) == tuple else other
		for key, val in [other for other in arr if len(other) == 2 and type(other) == tuple]:
			self[key] += val
		return self
