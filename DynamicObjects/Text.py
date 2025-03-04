import pygame
from DynamicObjects.AdaptingPlane import ReferencePlane
from StaticObjects.hid_Mouse import Mouse
from StaticObjects.hid_Keyboard import KeyBoard
from StaticObjects.Events import *
from SlotObjects.Verticies import Vertex
from SlotObjects.Pixel import *
pygame.font.init()

class TextBox:
	__slots__ = '_string', 'font', '_render', '_size', '_color'
	def __init__(self, string, font, color):
		self._color = color.__tuple__()
		self.font = [pygame.font.SysFont(font, i * 4) for i in range(1, 11)]
		self._size = []
		self._string = string
		self._render = None
		self.get_fit(Vertex(1, 1))

	@property
	def string(self):
		return self._string
	
	def __setattr__(self, key, val):
		if key == '_string':
			super().__setattr__(key, val)
			super().__setattr__('_size', [Vertex(*font.render(self.string, True, self._color).get_rect()[2:4]) for font in self.font])
		else:
			super().__setattr__(key, val)

	def get_fit(self, size, **kwargs):
		x = y = len(self._size) -1
		if kwargs.get('x', False):
			x = 1
			while self._size[x].x < size.x and x+1 < len(self._size):
				x += 1
		if kwargs.get('y', False):
			y = 1
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
		
class InputString:
	__slots__ = 'cursor_pos', 'blink', '_string', 'default', 'active'
	def __init__(self, default, interval):
		self.blink = [0, interval, False]
		self._string = [char for char in default]
		self.default = True
		self.active = False
		self.cursor_pos = 0
	
	def __setattr__(self, key, val):
		if key == 'cursor_pos':
			val = 0 if val < 0 else len(self._string) if val > len(self._string) else val
		super().__setattr__(key, val)
		
	def get_input(self, value=None):
		self._interval_counter()
		if value is None:
			return
		if not self.active:
			return
		if self.default:
			self.default = False
			self._string = ['', ]
		if len(value) == 1:
			print(KeyBoard.state_of('shift'))
			if KeyBoard.state_of('shift') != Hold:
				value = value.casefold()
			self._string.insert(self.cursor_pos, value)
			self.cursor_pos += 1
		else:
			cmd = {'backspace': self.backspace, 'delete': self.delete, 'left': self.left, 'right': self.right, 'home': self.home, 'end': self.end,
				   'return': self.enter}.get(value, None)
			if not cmd is None:
				cmd()

	def enter(self):
		self.active = False
		
	def home(self):
		self.cursor_pos = 0
	
	def end(self):
		self.cursor_pos = len(self._string)

	def backspace(self):
		if self.cursor_pos > 0:
			self.left()
			self._string.__delitem__(self.cursor_pos)
			
			#self.left()

	def delete(self):
		if self.cursor_pos < len(self._string) - 1:
			self._string.__delitem__(self.cursor_pos)
			
	def left(self):
		self.cursor_pos -= 1
		
	def right(self):
		self.cursor_pos += 1
		
	def _interval_counter(self):
		if self.active:
			self.blink[0] = (self.blink[0] + 1) % self.blink[1]
			self.blink[2] = not self.blink[2] if self.blink[0] == 0 else self.blink[2]

	
	@property
	def cursor(self):
		return ['_', ' '][self.blink[2]]

	@property
	def string(self):
		if self.default:
			return ''.join(self._string)
		else:
			temp = self._string.copy()
			if self.active:
				temp.insert(self.cursor_pos, self.cursor)
			return ''.join(temp)

class TextInput(TextBox):
	__slots__ = 'ref', '_string', 'font', '_render', '_size', '_color', 'bg_color'
	def __init__(self, ref:ReferencePlane, default:InputString, font, color, bg_color):
		self.ref = ref
		self.bg_color = bg_color
		super().__init__(default, font, color)
		self._size = [Vertex(*font.render(self.string, True, self._color).get_rect()[2:4]) for font in self.font]

	def activate(self):
		if Mouse.leftButton.state == Click:
			self._string.active = self.ref.click
		return self._string.active
	
	def update(self):
		if self.activate():
			[self._string.get_input(key) for key in KeyBoard.pressed()]
			self._size = [Vertex(*font.render(self.string, True, self._color).get_rect()[2:4]) for font in self.font]
	@property
	def string(self):
		return self._string.string
		
	def draw(self, surface):
		self.update()
		center = self.ref.related.abs_center(Vertex(0, 0))
		self.get_fit(self.ref.related.abs_size(Vertex(1, 1)), x=center.x, y=center.y)
		temp = center - self.ref.related.abs_size(Vertex(1, 1)) / 2
		pygame.draw.rect(surface, self.bg_color.__tuple__(), self.ref.to_rect)
		surface.blit(self.render, temp.__tuple__())
		
textinput_test = TextInput(ReferencePlane(Vertex(.0, .0), Vertex(.4, .1)), InputString('default', 30), 'arial', Pixel4(0, 255, 255, 244), Pixel3(128, 32, 32))
if __name__ == '__main__':
	pass
