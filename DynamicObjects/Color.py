from SlotObjects.Verticies import *
from SlotObjects.Pixel import *


class ColorFader(list):
	def __init__(self, *args, steps=30):
		self.position = 0
		self.state = None
		super().__init__([])
		assert all([isinstance(arg, Pixel3) for arg in args]) or all([isinstance(arg, Pixel4) for arg in args]), 'The Colors arent typed correct'
		for i, arg in enumerate(args[1:]):
			self += self.transition(args[i], arg, steps)
	
	def __getitem__(self, event=None):
		self.trigger(event)
		self.tick()
		return super().__getitem__(self.position).__tuple__()
	
	@property
	def iter_state(self):
		return {None: 0, True: 1, False:-1}[self.state]
	
	@staticmethod
	def transition(a, b, steps):
		temp = (b - a) / steps
		return [a + temp * i for i in range(steps-1)] + [b]
	
	def add_keycolor(self, color, steps):
		self += self.transition(self[-1], color, steps)

	def trigger(self, event=None):
		if event is None:
			return
		elif event and self.position < len(self) - 1:
			self.state = True
		elif not event and self.position > 0:
			self.state = False
		
	def tick(self):
		if 0 <= self.position + self.iter_state < len(self):
			self.position += self.iter_state
		else:
			self.state = None


class TargetColor:
	__slots__ = 'target', 'steps'
	
	def __init__(self, target, steps):
		self.target, self.steps = target, steps
		
	def que_from(self, current):
		if current != self.target:
			step = self.target - current * (1 / self.steps)
			return [current + step * i for i in range(self.steps)] + [self.target]
		else:
			return []
		

if __name__ == '__main__':
	temp = ColorFader(Pixel3.random(), Pixel3.random(), Pixel3.random())
	for i in range(1, 90):
		temp[None]
		if i % 5 == 0:
			print(temp[True])
		