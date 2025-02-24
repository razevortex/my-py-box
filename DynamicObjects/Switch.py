from DynamicObjects.MutaGen import *
from SlotObjects.Fetcher import FetcherObject


class SwitchSub(MuRectGen):
	def __init__(self, default:FetcherObject):
		pos = .25 if default else .75
		self._center = MuValGen((Vertex(pos, 0), 30))
		self._size = MuValGen((Vertex(1, 1), 30))
		self._color = MuValGen((Pixel4(196, 196, 196, 255), 30))
		self.fetch = default
		self.addEvent(True, 30, center=Vertex(-.25, -.25))
		self.addEvent(False, 30, center=Vertex(.25, -.25))
	
	def get_event(self, event=None):
		self._center.get_event(self.fetch.state)
		self._size.get_event(self.fetch.state)
		self._color.get_event(self.fetch.state)
	
	@property
	def center(self):
		return self.fetch.center + self.fetch.size * self._center.current
	
	@property
	def size(self):
		return self.fetch.half_size * self._size.current
	
	def draw(self, surface):
		self.get_event()
		args = self._color.current.__tuple__(), self.center, self.size
		rect = (args[1] - args[2] / 2).__tuple__() + args[2].__tuple__()
		pg.draw.rect(surface, args[0], pg.Rect(*rect))
		pg.draw.rect(surface, (32, 32, 32, 255), pg.Rect(*rect), width=2)
		
		
class SwitchMain:
	__slots__ = '_center', '_size', '_sub', 'state'
	
	def __init__(self, rel_center, rel_size, state=False):
		self._center = rel_center
		self._size = rel_size
		self.state = state
		self._sub = self.create_sub()
		
	def create_sub(self):
		return SwitchSub(FetcherObject(self, ['state', 'center', 'size', 'half_size']))
	
	@property
	def center(self):
		return AdaptingPlane.overlay.half_size + AdaptingPlane.overlay.half_size * self._center
	
	@property
	def size(self):
		return AdaptingPlane.overlay.fullsize * self._size
	
	@property
	def half_size(self):
		return self.size / 2
	
	def draw(self, surface):
		if self.click:
			self.state = not self.state
		temp = self.center - Vertex(abs(self.half_size.x), abs(self.half_size.y))
		temp2 = temp + Vertex(self.half_size.x, 0)
		border = pg.Rect(*(temp - 2).__tuple__() + ((self.size + 4).x, (self.half_size + 4).y))
		pg.draw.rect(surface, (32, 32, 32, 255), border)
		pg.draw.rect(surface, (255, 0, 0), pg.Rect(*temp.__tuple__() + self.half_size.__tuple__()))
		pg.draw.rect(surface, (0, 255, 0), pg.Rect(*temp2.__tuple__() + self.half_size.__tuple__()))
		self._sub.draw(surface)
		
	@property
	def hover(self):
		return self.center - self.half_size < Mouse.position < self.center + self.half_size
	
	@property
	def click(self):
		return self.hover and Mouse.leftButton.state.name == 'click'


if __name__ == '__main__':
	pass
