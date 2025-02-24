from SlotObjects.Verticies import Vertex
import mouse as hidM

class Hover:
	name = 'hover'
	
class Click:
	name = 'click'

class Drag:
	name = 'drag'

class Release:
	name = 'release'
	
class No:
	name = 'none'
	
class MBtn(list):
	def __init__(self, name):
		self.name = name
		super().__init__([False, False])
	
	@property
	def state(self):
		if all(self):
			return Drag
		elif any(self):
			return [Click, Release][self[1]]
		return No
	
	def update(self):
		print('update', hidM.is_pressed(button=self.name))
		if hidM.is_pressed(self.name):
			if not all(self):
				if self[0]: self[1] = True
				else: self[0] = True
			return
		else:
			if any(self):
				if self[0]: self[0] = False
				else: self[1] = False
			return
			

class Mouse:
	position = Vertex(*hidM.get_position())
	velocity = Vertex(0, 0)
	leftButton = MBtn('left')
	rightButton = MBtn('right')
	offset = None
	@classmethod
	def _pos(cls):
		if cls.offset is None:
			return Vertex(*hidM.get_position())
		else:
			return Vertex(*hidM.get_position()) - cls.offset.overlay.corners[0]
	@classmethod
	def update(cls):
		old = cls.position
		cls.position = cls._pos()
		cls.velocity = cls.position - old
		cls.leftButton.update()
		cls.rightButton.update()
	
	@classmethod
	def print(cls):
		print(f'{cls.position}\n{cls.leftButton.state}\n{cls.rightButton.state}')
	@classmethod
	def states(self):
		return self.position, self.leftButton, self.rightButton
	
# Execution Sandbox
if __name__ == '__main__':
	Mouse.update()
	while not all(Mouse.leftButton):
		Mouse.update()
		Mouse.print()
	while any(Mouse.leftButton):
		Mouse.update()
		Mouse.print()