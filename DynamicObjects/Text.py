import pygame
from SlotObjects.Verticies import Vertex
from SlotObjects.Pixel import *
pygame.font.init()

class TextBox:
	__slots__ = 'string', 'font', '_render', '_size', '_color'
	def __init__(self, string, font, color):
		self._color = color.__tuple__()
		self.font = [pygame.font.SysFont(font, i * 4) for i in range(1, 11)]
		self._size = []
		self.string = string
		self._render = None
		self.get_fit(Vertex(1, 1))

	def __setattr__(self, key, val):
		if key == 'string':
			super().__setattr__(key, val)
			super().__setattr__('_size', [Vertex(*font.render(self.string, True, self._color).get_rect()[2:4]) for font in self.font])
		else:
			super().__setattr__(key, val)

	def get_fit(self, size, **kwargs):
		x = y = len(self._size) -1
		if kwargs.get('x', False):
			x = 0
			while self._size[x].x < size.x and x+1 < len(self._size):
				x += 1
		if kwargs.get('y', False):
			y = 0
			while self._size[y].y < size.y and y+1 < len(self._size):
				y += 1
		self._render = self.font[min([x, y])].render(self.string, True, self._color)
	
	@property
	def render(self):
		return self._render
	
	@property
	def size(self):
		return Vertex(*self.render.get_rect()[2:4])
	
	def draw(self, surface, size, center):
		self.get_fit(size, x=center.x, y=center.y)
		temp = center - self.size / 2
		surface.blit(self.render, temp.__tuple__())
		

class TextBoxBG:
	__slots__ = 'string', 'font', '_render', '_size', '_color', '_bgcolor'
	
	def __init__(self, string, font, color, bg):
		super().__init__(string, font, color)
		self._bgcolor = bg
		
	def draw(self, surface, center, size):
		self.get_fit(size, x=center.x, y=center.y)
		temp = center - self.size / 2
		pg.draw.rect(surface, self._bgcolor, self.render.get_rect())
		surface.blit(self.render, temp.__tuple__())
		
if __name__ == '__main__':
	pass
