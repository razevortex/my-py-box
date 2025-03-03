from SlotObjects.Verticies import Vertex
from StaticObjects.Events import *
import keyboard as hidK


class Key(InputStateIO):
	_state = (No, Hold)
	_action = (Release, Press)
	
	def __init__(self, name):
		super().__init__(name)
		self.name = name + '_KEY'
		self.status = self._state[0]
	
	@property
	def check(self):
		return self._action[hidK.is_pressed(self.name[:-4])]
	
	def update_status(self):
		self._update_status(got=self.check)
		

class KeyBoard


if __name__ == '__main__':
	pass
