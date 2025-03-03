from DynamicObjects.MutaGen import *
from SlotObjects.Fetcher import FetcherObject
from DynamicObjects.AdaptingPlane import ReferencePlane
from DynamicObjects.Text import TextBox, TextBoxBG

class Items(list):
	def __init__(self, *args, default=0):
		self.selection = default
		self.start = default + 1
		self.next_btn = TextBox('<...>', 'arial', Pixel4(192, 192, 255, 255))
		super().__init__([TextBox(selectable, 'arial', Pixel4(0, 0, 255, 255)) for selectable in args])

	def move_start(self, value):
		if self.start + value != 0:
			self.start = (self.start + value) % len(self)
		
	def select(self, value):
		if value != 0:
			self.selection = (self.start + value - 1) % len(self)
	
	@property
	def fulllist(self):
		return [self[self.selection], ] + self[self.start:] + self[:self.start] + [self.next_btn, ]
	
	def get(self, n):
		return self.fulllist[:n] if n == 1 else self.fulllist[:n-1] + [self.next_btn, ]
	
	@property
	def current(self):
		return self[self.selection].string
	
class BG:
	__slots__ = '_center', '_size', '_color', 'ref'
	
	def __init__(self, center, size, color, ref):
		self._center = center
		self._size = size
		self._color = color
		self.ref = ref
	
	@property
	def color(self):
		return [self._color, Pixel3(192, 192, 192)][self.hover]
	
	@property
	def child(self):
		class _child(self.__class__):
			@property
			def center(self):
				return self._center
			@property
			def size(self):
				return self._size
			
			def draw(self, surface):
				pg.draw.rect(surface, self.color.__tuple__(), self.rect)
				pg.draw.polygon(surface, Pixel3(32, 32, 32).__tuple__(), self.outline, width=2)
		
		return _child

	def adhesiv_generator(self, direction='S'):
		def gen():
			if direction == 'S':
				yield self.child(self.center, self.size, self._color, None)
				center, size, color = self.center, self.size, self._color
				while True:
					center += Vertex(0, self.size.y)
					yield self.child(center, size, color, None)
		return gen()
		
	@property
	def center(self):
		return self.ref.abs_center(self._center)
	
	@property
	def size(self):
		return self.ref.abs_size(self._size)
	
	@property
	def outline(self):
		lt = self.center - self.size / 2
		rb = lt + self.size
		rt = Vertex(rb.x, lt.y)
		lb = Vertex(lt.x, rb.y)
		return lt.__tuple__(), rt.__tuple__(), rb.__tuple__(), lb.__tuple__()
	
	@property
	def rect(self):
		temp = self.center - self.size / 2
		return pg.Rect(*temp.__tuple__() + self.size.__tuple__())
	
	def draw(self, surface):
		pg.draw.rect(surface, self._color.__tuple__(), self.rect)
		pg.draw.polygon(surface, Pixel3(32, 32, 32).__tuple__(), self.outline, width=2)
		
	@property
	def hover(self):
		return self.center - self.size / 2 < Mouse.position < self.center + self.size / 2
	
	@property
	def click(self):
		return self.hover and Mouse.leftButton.state.name == 'click'
	
class Selection:
	__slots__ = 'ref', 'selectables', 'bg1', 'state', '_n_items'
	def __init__(self, selectables, center=Vertex(0, -.95), size=Vertex(.05, .05), selected=0, n_items=5):

		self._n_items = n_items
		self.selectables = Items(*selectables, default=selected)
		self.ref = ReferencePlane(center, size)
		self.bg1 = BG(Vertex(0, 0), Vertex(1, 1), Pixel3(128, 128, 0), self.ref.related)
		self.state = False
		
	@property
	def n_items(self):
		if self.state:
			return min([self._n_items, len(self.selectables) - 1]) + 1
		else:
			return 1
		
	@property
	def selected(self):
		return self.selectables.current.string

	def check_events(self):
		temp = self.bg1.adhesiv_generator()
		bgs = [next(temp) for i in range(self.n_items)]
		self.state = any([bg.hover for bg in bgs])
		if self.state:
			for i, bg in enumerate(bgs):
				#print(f'{i} => hover => {bg.hover}')
				if bg.click:
					if i < len(bgs) - 1:
						print(f'clicked {i} when start {self.selectables.start} of {len(self.selectables)}')
						self.selectables.select(i)
						print(f'resulting in selected {self.selectables.start} => {self.selectables.current}')
						return
					else:
						self.selectables.move_start(i)
						return
					
	def draw(self, surface):
		self.check_events()
		temp = self.bg1.adhesiv_generator()
		bgs = [next(temp) for i in range(self.n_items)]
		items = self.selectables.get(self.n_items)
		for bg, item in zip(bgs, items):
			bg.draw(surface)
			item.draw(surface, bg.size, bg.center)
			
			
if __name__ == '__main__':
	pass
