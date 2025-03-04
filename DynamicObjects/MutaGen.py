from SlotObjects.Pixel import *
from StaticObjects.hid_Mouse import *
from DynamicObjects.AdaptingPlane import AdaptingPlane, ReferencePlane
import pygame as pg
Mouse.offset = AdaptingPlane


class MuValGen:
	__slots__ = '_gen', 'last_event', 'event_dict'
	
	def __init__(self, default, **kwargs):
		self.event_dict = {None: default}
		self.event_dict.update(kwargs)
		self.last_event = None
		self._gen = self._create_generator(self.get_static_gen(self.event_dict.get(self.last_event)))
	
	def add_event(self, key, value):
		assert isinstance(value[0], type(self.event_dict.get(None)[0])), 'type error'
		self.event_dict[key] = value
	
	def get_static_gen(self, value: tuple):
		value, _ = value
		
		def gen(value):
			while True:
				yield value
		
		return gen(value)
	
	def set_dynamic_gen(self):
		start = self.current
		end, steps = self.event_dict.get(self.last_event)
		step = (end - start) / steps
		
		def new_gen(start, end, steps, step):
			steps -= 1
			while steps > 0:
				start += step
				yield start
				steps -= 1
			yield end
		
		self._gen = self._create_generator(original_gen=new_gen(start, end, steps, step))
	
	def get_event(self, event=None):
		if self.last_event != event:
			self.last_event = event
			if self.event_dict.get(self.last_event, False):
				self.set_dynamic_gen()
	
	def _create_generator(self, original_gen=None, value=None):
		assert original_gen is not None or value is not None, 'Either original_gen or value must be provided'
		if original_gen is None:
			while True:
				yield value
		else:
			last_value = None
			exhausted = False
		while True:
			if not exhausted:
				try:
					last_value = next(original_gen)
				except StopIteration:
					exhausted = True
					if last_value is None:
						return  # Raise StopIteration if no elements were generated
				else:
					yield last_value
			else:
				yield last_value
	
	@property
	def current(self):
		return next(self._gen)


class RelativeMutableCenterGenerator(MuValGen):
	__slots__ = '_gen', 'last_event', 'event_dict', 'reference'
	
	def __init__(self, default, reference:ReferencePlane, **kwargs):
		super().__init__(default, **kwargs)
		self.reference = reference.related	


class MuCircleGen:
	__slots__ = '_center', '_radius', '_color'
	
	def __init__(self, rel_center, rel_radius, color, frames=30):
		'''
        rel_center: Vertex
        rel_radius: Vertex
        color: Pixel
        frames: int
        '''
		self._center = MuValGen((rel_center, frames))
		self._radius = MuValGen((rel_radius, frames))
		self._color = MuValGen((color, frames))
	
	def addEvent(self, event, frames, center=None, radius=None, color=None):
		kwargs = {'_center': (center, frames), '_radius': (radius, frames), '_color': (color, frames)}
		[self.__getattribute__(key).add_event(event, val) for key, val in kwargs.items() if val[0] is not None]
	
	def get_event(self, event=None):
		print(self.event)
		self._center.get_event(self.event)
		self._radius.get_event(self.event)
		self._color.get_event(self.event)
	
	@property
	def center(self):
		return AdaptingPlane.overlay.half_size + AdaptingPlane.overlay.half_size * self._center.current
	
	@property
	def radius(self):
		return AdaptingPlane.overlay.fullsize * self._radius.current

	@property
	def event(self):
		return None if not self.hover else 'hover' if not self.click else 'click' if not self.drag else 'drag'
	
	@property
	def hover(self):
		return self.center.distance(Mouse.position) <= self.radius.x
	
	@property
	def click(self):
		return self.hover and Mouse.leftButton.state.name == 'click'
	
	@property
	def drag(self):
		return self.hover and Mouse.leftButton.state.name == 'drag'
	
	def draw(self, surface):
		self.get_event()
		args = self._color.current.__tuple__(), self.center.__tuple__(), int(self.radius.x)
		[print(arg) for arg in args]
		pg.draw.circle(surface, *args)

	@property
	def current(self):
		return self._center.current, self._radius.current, self._color.current


class MuRectGen(MuCircleGen):
	__slots__ = '_center', '_size', '_color'
	
	def __init__(self, rel_center, rel_size, color, frames):
		'''
		rel_center: Vertex
		rel_radius: Vertex
		color: Pixel
		frames: int
		'''
		self._center = MuValGen((rel_center, frames))
		self._size = MuValGen((rel_size, frames))
		self._color = MuValGen((color, frames))
	
	def addEvent(self, event, frames, center=None, size=None, color=None):
		kwargs = {'_center': (center, frames), '_sizr': (size, frames), '_color': (color, frames)}
		[self.__getattribute__(key).add_event(event, val) for key, val in kwargs.items() if val[0] is not None]

	def get_event(self, event=None):
		print(self.event)
		self._center.get_event(self.event)
		self._size.get_event(self.event)
		self._color.get_event(self.event)
		
	@property
	def size(self):
		return AdaptingPlane.overlay.fullsize * self._size.current
	
	def draw(self, surface):
		self.get_event()
		args = self._color.current.__tuple__(), self.center, self.size
		rect = (args[1] - args[2] / 2).__tuple__() + args[2].__tuple__()
		pg.draw.rect(surface, args[0], pg.Rect(*rect))



if __name__ == '__main__':
	test = MuCircleGen(Vertex(0, 0), Vertex(.1, 0), Pixel4(0, 0, 255, 255), 30)
	test.addEvent('hover', 20, center=Vertex(.5, .5), radius=Vertex(.5, 0), color=Pixel4(127, 127, 127, 255))
	for i in range(30):
		if i == 2:
			test.get_event('hover')
		if i == 20:
			test.get_event('click')
		print([item for item in test.current])
