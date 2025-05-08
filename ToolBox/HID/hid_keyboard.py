import keyboard
import time
from json import loads
from enum import Enum, Flag, auto
import dataclasses
import threading


class MK(Flag):
	CTRL = auto()
	ALT = auto()
	SHIFT = auto()

class StatesMK(dict):
	_checks = {MK.CTRL: (29,), MK.ALT: (56, 541), MK.SHIFT: (42,)}
	
	def __init__(self):
		super().__init__({key: any([keyboard.is_pressed(v) for v in val]) for key, val in self._checks.items()})
	
	@property
	def active(self):
		return [key for key, val in self.items() if val]

class CK(Enum):
	BACKSPACE = 3
	POS1 = 4
	END = 5
	DEL = 6
	INS = 7
	PAGE_UP = 8
	PAGE_DOWN = 9
	LEFT = 10
	RIGHT = 11
	UP = 12
	DOWN = 13
	ESC = 14
	SPACE = 15
	TAB = 16
	ENTER = 17


@dataclasses.dataclass
class KeyEvent:
	key: CK
	mods: StatesMK


@dataclasses.dataclass
class CHAR:
	base: str|None
	shift: str|None
	alt: str|None
	code: int


@dataclasses.dataclass
class CharEvent:
	key: CHAR
	mods: StatesMK


class StatesCK:
	_checks = {
		CK.BACKSPACE: 14, CK.POS1: 71, CK.END: 79, CK.DEL: 83, CK.INS: 82, CK.PAGE_UP: 73,
		CK.PAGE_DOWN: 81, CK.LEFT: 75, CK.RIGHT: 77, CK.UP: 72, CK.DOWN: 80, CK.ESC: 1,
		CK.SPACE    : 57, CK.TAB: 15, CK.ENTER: 28}
	
	def __init__(self):
		self.pressed = []
	
	def handle_press(self, event):
		for key, val in self._checks.items():
			if val == event.scan_code and key not in self.pressed:
				self.pressed.append(key)
				return KeyEvent(key, StatesMK())
		return None
	
	def handle_release(self, event):
		if event.scan_code in self._checks.values():
			try:
				for key, val in self._checks.items():
					if val == event.scan_code:
						self.pressed.remove(key)
						return
			except:
				print('something went wrong')


class BaseCK:
	_checks = 'ScanKeyCode.json'
	
	def __init__(self):
		self._import()
		self.pressed = []

	def _import(self):
		temp = []
		with open(self._checks, 'r') as f:
			for item in loads(f.read()):
				temp.append(CHAR(base=item['base'], shift=item['shift'], alt=item['alt'], code=item['code']))
		self._checks = temp

	@property
	def code_list(self):
		return [dic.code for dic in self._checks]

	def handle_pressed(self, event):
		if event.scan_code in self.code_list:
			i = self.code_list.index(event.scan_code)
			if i not in self.pressed:
				self.pressed.append(i)
				return CharEvent(self._checks[i], StatesMK())
		return None
	
	def handle_release(self, event):
		if event.scan_code in self.pressed:
			self.pressed.remove(event.scan_code)


class KeyboardHandle:
	register = []
	
	def __init__(self):
		self.controlKeys = StatesCK()
		self.charKeys = BaseCK()
		self.threads = keyboard.hook(callback=self._change)
		self._getter = self._get()
	
	def _change(self, event):
		if event.event_type == 'down':
			if self.controlKeys.handle_press(event):
				self.register.append(self.controlKeys.handle_press(event))
	
	def _get(self):
		while True:
			if self.register:
				yield self.register.pop(0)
			yield None
	
	@property
	def getter(self):
		return next(self._getter)


test = StatesCK()

def _is_pressed(event):
	if test.handle_press(event):
		print(test.handle_press(event))

# print(keyboard.is_pressed(event.scan_code))
# print(event.name, event.event_type, event.scan_code)


def mk(event_code):
	if event_code in (42, 54, 56, 541):
		pass

if __name__ == '__main__':
	# print([chr(i) for i in range(128)])
	# keyboard.hook(callback=_change)
	kh = KeyboardHandle()
	while True:
		temp = kh.getter
		if temp is not None:
			print(temp)


