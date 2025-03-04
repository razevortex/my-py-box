import win32com.client
import win32gui
from SlotObjects.Fetcher import *
from StaticObjects.hid_Mouse import *
from StaticObjects.Events import *


class window:
	def __init__(self, name):
		self.name = name
	
	@property
	def id(self):
		return win32gui.FindWindow(None, self.name)
		
	@property
	def _rect(self):
		return win32gui.GetWindowRect(self.id)
	@property
	def center(self):
		return (Vertex(*self._rect[:2]) + Vertex(*self._rect[2:])) / 2
	@property
	def half_size(self):
		return Vertex(*self._rect[2:]) - self.center
	@property
	def fullsize(self):
		return self.half_size * 2
	@property
	def w(self):
		return int(self.fullsize.x)
	@property
	def h(self):
		return int(self.fullsize.y)
	@property
	def corners(self):
		l, t, r, b = self._rect
		return Vertex(l, t), Vertex(r, t), Vertex(r, b), Vertex(l, b)
	
	@property
	def is_active(self):
		 return self.id == win32gui.GetForegroundWindow()
	
	def arrange(self, _rect):
		#assert isinstance(_rect, cls.__class__), f'_rect of type {type(_rect)} is not the expected type'
		x, y = _rect.corners[0].__tuple__()
		win32gui.MoveWindow(self.id, x, y, _rect.w, _rect.h, True)

	def push_to_forground(self):
		shell = win32com.client.Dispatch("WScript.Shell")
		shell.SendKeys('%')
		win32gui.SetForegroundWindow(self.id)


class AdaptingPlane:
	target = None
	overlay = None
	last_target_rect = None
	
	@classmethod
	def setup_window(cls, target, overlay):
		cls.target = window(target)
		cls.last_target_rect = cls.target._rect
		cls.overlay = window(overlay)
	
	@classmethod
	def _align(cls):
		if cls.last_target_rect != cls.target._rect:
			cls.last_target_rect = cls.target._rect
			cls.overlay.arrange(cls.target)
			cls.overlay.push_to_forground()


Mouse.offset = AdaptingPlane


class ReferencePlane:
	__slots__ = '_center', '_size', 'related', 'active'

	def __init__(self, rel_center, rel_size, active=True):
		self._center = rel_center
		self._size = rel_size
		self.related = FetchRef(self)
		self.active = active

	def __repr__(self):
		return f'hover:{self.hover}, click:{self.click}, drag:{self.drag}\n{self.center - self.size / 2}, {Mouse.position}, {self.center + self.size / 2}'

	@property
	def center(self):
		return AdaptingPlane.overlay.half_size + AdaptingPlane.overlay.half_size * self._center
	
	@property
	def size(self):
		return AdaptingPlane.overlay.fullsize * self._size
	
	@property
	def half_size(self):
		return self.size / 2
	
	@property
	def to_rect(self):
		temp = self.center - self.half_size
		return temp.x, temp.y, self.size.x, self.size.y
	
	@property
	def hover(self):
		return self.center - self.half_size < Mouse.position < self.center + self.half_size
	
	@property
	def click(self):
		return self.hover and Mouse.leftButton.state == Click
	
	@property
	def drag(self):
		return self.hover and Mouse.leftButton.state == Drag



if __name__ == '__main__':
	pass