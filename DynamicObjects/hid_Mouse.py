from SlotObjects.Verticies import Vertex
from StaticObjects.Events import *
import mouse as hidM


class MouseButton(InputStateIO):
	_state = (No, Drag)
	_action = (Release, Click)

	def __init__(self, name):
		super().__init__(name)
		self.name = name + 'Button'
		self.status = self._state[0]

	@property
	def check(self):
		return self._action[hidM.is_pressed(self.name[:-6])]
	
	def update_status(self):
		self._update_status(got=self.check)


'''class MBtn(list):
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
	def states(cls):
		return cls.position, cls.leftButton, cls.rightButton'''
	
	
class Mouse:
	position = Vertex(*hidM.get_position())
	velocity = Vertex(0, 0)
	offset = None
	leftBtn = MouseButton('left')
	rightBtn = MouseButton('right')
	
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
		cls.leftBtn.update_status()
		cls.rightBtn.update_status()
		
	@classmethod
	def show(cls):
		print(f'{cls.leftBtn.name} : {cls.leftBtn.status}')
		print(f'{cls.rightBtn.name} : {cls.rightBtn.status}')
		
		
# Execution Sandbox
if __name__ == '__main__':
	import time
	while True:
		Mouse.update()
		Mouse.show()
		time.sleep(1)
	'''Mouse.update()
	while not all(Mouse.leftButton):
		Mouse.update()
		Mouse.print()
	while any(Mouse.leftButton):
		Mouse.update()
		Mouse.print()'''
