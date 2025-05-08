import keyboard
import time
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
	
	
class StatesCK:
	_checks = {
		CK.BACKSPACE: 14, CK.POS1: 71, CK.END: 79, CK.DEL: 83, CK.INS: 82, CK.PAGE_UP: 73,
		CK.PAGE_DOWN: 81, CK.LEFT: 75, CK.RIGHT: 77, CK.UP: 72, CK.DOWN: 80, CK.ESC: 1,
		CK.SPACE: 57, CK.TAB: 15, CK.ENTER: 28}

	def __init__(self):
		self.pressed = []
	
	def handle_press(self, event):
		for key, val in self._checks.items():
			if val == event.scan_code and key not in self.pressed:
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
		

class KeyboardHandle:
	register = []
	def __init__(self):
		self.controlKeys = StatesCK()
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
	

"""import mouse
from SlotObjects.Verticies import *
from time import perf_counter_ns as nsec
import threading

class MouseTimer:
    def __init__(self):
        self.start = None

    @property
    def running(self):
        return not self.start is None

    @property
    def duration(self):
        if self.start is not None:
            return (nsec() - self.start) * 10 ** -9
        else:
            return None

    def stop_clk(self):
        self.start = None

    def start_clk(self):
        self.start = nsec()

    def check_clk(self, time, set_to=None):
        if self.start is not None:
            print(self.duration)
            if self.duration >= time:
                self.start = set_to
                return True
        return False

class State:
    __slots__ = 'name', 'event', 'time'
    def __new__(cls, name, event):
        new = super().__new__()
        new.name = name
        new.event = event
        return new

    def __init__(self, *args):
        self.time = None

    @property
    def state(self):
        if self.time is not None:
            if self.duration > .2 and not mouse.is_pressed(self.name):
                self.time = None
                return 'click', Vertex(*mouse.get_position())
            elif self.duration > .2 and mouse.is_pressed(self.name):
                return 'hold', Vertex(*mouse.get_position())

    def _button_handle(self, event):
        if event.button == self.event:
            if event.event_type == mouse.DOWN:
                self.time = nsec()


            self.state = event.event_type == mouse.DOWN, (nsec() - self.time) * 10 ** -9 < .2
            if self.state[0]:
                self.time = nsec()

    def check_time(self):
        if self.time is not None:
            if self.duration > .25:
                if all(self.state):
                    self.action = 'x2'
                    self.time = None
                elif any(self.state):
    @property
    def duration(self):
        return (nsec() - self.time) * 10 ** -9
    def reset(self):
        pos = self.pos
        self.pressing = False
        self.click = False
        self.hold = False
        self.pos = None
        self.clock.stop_clk()
        return pos

    def __repr__(self):
        return f'p {self.pressing}, c {self.click}, h {self.hold}, l {self.pos}, t {self.clock.duration}'

    @property
    def pos_delta(self):
        pos = self.pos
        self.pos = mouse.get_position()
        return pos, self.pos

    def state(self, state):
        if state is None: # None is passed if timer ran out
            if self.click:
                return 'click', self.reset()
            elif self.pressing:
                self.hold, self.pressing = True, False
            return None
        elif self.hold:
            if not state:
                return 'release', self.reset()
            else:
                return 'hold', self.pos_delta

        elif self.pressing is not state:
            if self.pressing:
                #if self.click:
                #	return 'x2', self.reset()
                self.click = self.pressing
                self.pressing = not self.pressing
                #self.pressing, self.click = False, True
                return None
            elif not self.pressing:
                print(f'!press {state} -> click = {self.click}')
                self.pressing = True
                if not self.click:
                    self.pos = mouse.get_position()
                    self.clock.start_clk()
                if self.click:
                    return 'x2', self.reset()
                return None

    def check(self, state):
        if self.clock.check_clk(.5):
            return self.state(None)
        else:
            return self.state(state)

class Button:
    __slots__ = 'name', 'state', 'timer', 'durations'
    def __init__(self, btn):
        self.name = btn
        self.state = State()

    @property
    def event(self):
        got = self.state.check(mouse.is_pressed(button=self.name))
        if not got is None:
            print(self.state, got)
        return got



class MouseHandle:
    __slots__ = 'frame', 'button', 'area', 'timer'
    def __init__(self, frame, areas):
        pass
# Execution Sandbox

if __name__ == '__main__':
    import time
    test = Button('left')
    while True:
        temp = test.event
        time.sleep(.05)
"""
'''from dataclasses import dataclass, field
from enum import Enum, auto
import time
import queue
from typing import Optional, Tuple, Dict
from pynput import mouse
from pynput.mouse import Button, Controller
import threading


class EventType(Enum):
	CLICK = auto()
	DOUBLE_CLICK = auto()
	HOLD_START = auto()
	HOLD_UPDATE = auto()
	HOLD_END = auto()

class ButtonType(Enum):
	LEFT = auto()
	MIDDLE = auto()
	RIGHT = auto()

@dataclass
class MouseEvent:
	button: ButtonType
	event_type: EventType
	abs_position: Tuple[int, int]
	position_delta: Tuple[int, int]
	timestamp: float

@dataclass
class ButtonState:
	pressed: bool = False
	start_time: Optional[float] = None
	start_pos: Optional[Tuple[int, int]] = None
	last_event_type: Optional[EventType] = None
	current_pos: Optional[Tuple[int, int]] = None
	last_event_time: Optional[float] = None

class MouseEventHandler:
	def __init__(
		self,
		click_duration: float = 0.2,
		double_click_interval: float = 0.15,
		poll_interval: float = 0.01
		):
		self.click_duration = click_duration
		self.double_click_interval = double_click_interval
		self.poll_interval = poll_interval
		
		self.button_states: Dict[ButtonType, ButtonState] = {
			ButtonType.LEFT  : ButtonState(),
			ButtonType.MIDDLE: ButtonState(),
			ButtonType.RIGHT : ButtonState()
			}
		
		self.event_queue = queue.Queue()
		self._listener: Optional[mouse.Listener] = None
		self._controller = Controller()
		self._lock = threading.RLock()
		
		self._setup_windows_coordinates()
	
	def tick(self):
		for state in self.button_states.values():
			if state.last_event_time:
				if time.time() - state.last_event_time > .25:
					if state.last_event_type == EventType.CLICK:
						self.event_queue.put(MouseEvent(
							button=self._get_button_type(state),
							event_type=EventType.CLICK,
							abs_position=state.start_pos,
							position_delta=(0, 0),
							timestamp=state.last_event_time
							)
							)
						state.last_event_time = None
					elif state.last_event_type == EventType.DOUBLE_CLICK:
						self.event_queue.put(MouseEvent(
							button=self._get_button_type(state),
							event_type=EventType.DOUBLE_CLICK,
							abs_position=state.start_pos,
							position_delta=(0, 0),
							timestamp=state.last_event_time
							)
							)
						state.last_event_time = None
					elif state.pressed and state.start_pos is not None:
						dx = x - state.current_pos[0]
						dy = y - state.current_pos[1]
						btn_state.current_pos = (x, y)
						
						if btn_state.last_event_type == EventType.HOLD_START:
							self.event_queue.put(MouseEvent(
								button=self._get_button_type(btn_state),
								event_type=EventType.HOLD_UPDATE,
								abs_position=(x, y),
								position_delta=(dx, dy),
								timestamp=current_time
								)
								)
	
	def _setup_windows_coordinates(self):
		"""Initialize screen metrics with pywin32 if available, fallback to pynput"""
		try:
			from win32api import GetSystemMetrics
			self.screen_width = GetSystemMetrics(0)
			self.screen_height = GetSystemMetrics(1)
			self._using_precise_metrics = True
		except ImportError:
			print("Warning: pywin32 not installed - using pynput's screen metrics. For precise Windows coordinates:")
			print("  pip install pywin32")
			self.screen_width, self.screen_height = self._controller.screen_size
			self._using_precise_metrics = False
	
	def _button_type_from_pynput(self, button: Button) -> ButtonType:
		return {
			Button.left  : ButtonType.LEFT,
			Button.middle: ButtonType.MIDDLE,
			Button.right : ButtonType.RIGHT
			}[button]
	
	def _on_move(self, x: int, y: int):
		with self._lock:
			current_time = time.time()
			for btn_state in self.button_states.values():
				if btn_state.pressed and btn_state.start_pos is not None:
					dx = x - btn_state.current_pos[0]
					dy = y - btn_state.current_pos[1]
					btn_state.current_pos = (x, y)
					
					if btn_state.last_event_type == EventType.HOLD_START:
						self.event_queue.put(MouseEvent(
							button=self._get_button_type(btn_state),
							event_type=EventType.HOLD_UPDATE,
							abs_position=(x, y),
							position_delta=(dx, dy),
							timestamp=current_time
							)
							)
	
	def _on_click(self, x: int, y: int, button: Button, pressed: bool):
		with self._lock:
			current_time = time.time()
			btn_type = self._button_type_from_pynput(button)
			btn_state = self.button_states[btn_type]
			if btn_state.last_event_time:
				if current_time - btn_state.last_event_time >= self.click_duration:
					if btn_state.last_event_type == EventType.CLICK:
			if pressed:
				self._handle_press(btn_state, x, y, current_time)
			else:
				self._handle_release(btn_state, x, y, current_time)
			
			btn_state.current_pos = (x, y)
	
	def _handle_press(self, btn_state: ButtonState, x: int, y: int, timestamp: float):
		if not btn_state.pressed:
			btn_state.pressed = True
			btn_state.start_time = timestamp
			btn_state.start_pos = (x, y)
			btn_state.current_pos = (x, y)
			
			if (btn_state.last_event_time and
				(timestamp - btn_state.last_event_time) <= self.double_click_interval and
				btn_state.last_event_type == EventType.CLICK):
				self.event_queue.put(MouseEvent(
					button=self._get_button_type(btn_state),
					event_type=EventType.DOUBLE_CLICK,
					abs_position=(x, y),
					position_delta=(0, 0),
					timestamp=timestamp
					)
					)
				btn_state.last_event_type = EventType.DOUBLE_CLICK
			else:
				btn_state.last_event_type = EventType.HOLD_START
				self.event_queue.put(MouseEvent(
					button=self._get_button_type(btn_state),
					event_type=EventType.HOLD_START,
					abs_position=(x, y),
					position_delta=(0, 0),
					timestamp=timestamp
					)
					)
	
	def _handle_release(self, btn_state: ButtonState, x: int, y: int, timestamp: float):
		if btn_state.pressed:
			btn_state.pressed = False
			duration = timestamp - btn_state.start_time
			
			if duration <= self.click_duration:
				if btn_state.last_event_type != EventType.DOUBLE_CLICK:
					self.event_queue.put(MouseEvent(
						button=self._get_button_type(btn_state),
						event_type=EventType.CLICK,
						abs_position=(x, y),
						position_delta=self._calculate_delta(btn_state, x, y),
						timestamp=timestamp
						)
						)
					btn_state.last_event_type = EventType.CLICK
			
			self.event_queue.put(MouseEvent(
				button=self._get_button_type(btn_state),
				event_type=EventType.HOLD_END,
				abs_position=(x, y),
				position_delta=self._calculate_delta(btn_state, x, y),
				timestamp=timestamp
				)
				)
			
			btn_state.last_event_time = timestamp
			btn_state.start_time = None
			btn_state.start_pos = None
	
	def _calculate_delta(self, btn_state: ButtonState, x: int, y: int) -> Tuple[int, int]:
		"""Calculate position delta with platform-aware coordinate interpretation"""
		if btn_state.start_pos:
			# Account for Windows coordinate system origin (upper-left corner)
			base_x, base_y = btn_state.start_pos
			# Windows Y axis goes downward, maintain positive deltas for downward movement
			return (x - base_x, y - base_y)
		return (0, 0)
	
	def _get_button_type(self, btn_state: ButtonState) -> ButtonType:
		with self._lock:
			return next(
				k for k, v in self.button_states.items()
				if v is btn_state
				)
	
	def start_listening(self):
		"""Start mouse listener in background thread"""
		self._listener = mouse.Listener(
			on_click=self._on_click,
			on_move=self._on_move
			)
		self._listener.daemon = True
		self._listener.start()
	
	def stop_listening(self):
		"""Stop mouse listener"""
		if self._listener and self._listener.is_alive():
			self._listener.stop()'''

test = StatesCK()

def _is_pressed(event):
	if test.handle_press(event):
	
		print(test.handle_press(event))
	#print(keyboard.is_pressed(event.scan_code))
	#print(event.name, event.event_type, event.scan_code)
	
def mk(event_code):
	if event_code in (42, 54, 56, 541):
		pass
if __name__ == '__main__':
	#print([chr(i) for i in range(128)])
	#keyboard.hook(callback=_change)
	kh = KeyboardHandle()
	while True:
		temp = kh.getter
		if temp is not None:
			print(temp)
		
		
		
