class ValueRange:
	__slots__ = 'start', 'end', 'value', 'iter'
	def __init__(self, start=0, end=100, value=0, iter=1):
		assert (end - start) % iter == 0, f'end {end} needs to be divisable by {iter}' 
		[self.__setattribute__(slot, kwargs.get(slot)) for slot in self.__slots__)]

	def __setattribute__(self, slot, val):
		if slot == 'value':
			val = self.start if val < self.start else self.end if val > self.end else val
			val = 0 if val == 0 else val // self.iter * self.iter
			if not (self[0] <= val < self[2]):
				val = self[0] if self[0] > val else self[2] - 1
		super().__setattribute__(slot, val)
		
	def __len__(self):
		return self.distance // self.iter

	@property
	def distance(self):
		return self.end - self.start
	@property
	def step_n(self):
		return 0 if self.value == 0 else self.value // self.step_size

	@property
	def rel_pos(self):
		return self.value / self.distance

	@pos.setattr
	def rel_pos(self, val):
		'''
  		uses the relative position to get the value
    		if in some gui a slider would be used 
      		along its line from x0 to x1, x1 - x0 divided by the X position of the slider
		the alignment to the stepsize is handled by the __setattr__  
  		'''
		self.value = self.distance * val + self.start
