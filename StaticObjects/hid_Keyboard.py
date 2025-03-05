from SlotObjects.Verticies import Vertex
from StaticObjects.Events import *
import keyboard as hidK


class Key(InputStateIO):
	_state = (No, Hold)
	_action = (Release, Press)
	
	def __init__(self, name, _doubled=None):
		super().__init__(name)
		if isinstance(name, tuple):
			name, _doubled = name
		self.name = name + '_KEY'
		self.state = self._state[0]
		self._doubled = _doubled
	
	@property
	def doubled(self):
		return False if self._doubled is None else hidK.is_pressed(self._doubled)
	
	@property
	def check(self):
		if not self.doubled:
			return self._action[hidK.is_pressed(self.name[:-4])]
	
	def update_status(self):
		self._update_status(got=self.check)
		

char_set = ['0', '1', ('2', 'down'), '3', ('4', 'left'), '5', ('6', 'right'), '7', ('8','up'), '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
			'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'escape', 'space', 'backspace', 'tab', 'linefeed', 'clear', 'return',
			'pause', 'scroll_lock', 'delete', 'home', 'left', 'up', 'right', 'down', 'page_up', 'page_down', 'end', 'print', 'insert',
			'num_lock', 'shift', 'ctrl', 'alt']

class KeyBoard:
	keys = [Key(char) for char in char_set]
	
	@classmethod
	def update(cls):
		[key.update_status() for key in cls.keys]
		
	@classmethod
	def pressed(cls):
		temp = [key.name.rstrip('_KEY') for key in cls.keys if key.state == Press]
		print(temp)
		return [None, ] if temp == [] else temp
		
	@classmethod
	def state_of(cls, key):
		for k in cls.keys:
			if k.name.startswith(key):
				return k.state
			
def test():
	last_state = [key.status for key in KeyBoard.keys]
	while True:
		KeyBoard.update()
		i = 0
		for last, key in zip(last_state, KeyBoard.keys):
			if last != key.status:
				print(f'{key.name} => {key.status}')
			last_state[i] = key.status
			i += 1

if __name__ == '__main__':
	test()
	#keys = [chr(val) for val in [range_ for range_ in [range(48, 58), range(65, 91), range(97, 123)]]]
	#keys = [chr(val) for val in range(33, 127)]
	#string =  '\` ~ ! @ # $ % ^ & \* ( ) - _ + = [ ] { } \\ | ; : ' " / ? . > , <'
	#words = ('Escape, Space, BackSpace, Tab, Linefeed, Clear, Return, Pause, Scroll_Lock, Sys_Req, Delete, Home, Left, Up, Right, Down, Prior, Page_Up, Next, '
	#  'Page_Down, End, Begin, Select, Print, Execute, Insert, Undo, Redo, Menu, Find, Cancel, Help, Break, Mode_switch, script_switch, Num_Lock,').split(',')
	#keys += [word.strip().casefold() for word in words]
	#print(keys)