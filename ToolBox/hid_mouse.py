import mouse
import time
from enum import Enum
import dataclasses
import threading

class Events(Enum):
    _NONE = 0
    CLICK = 1
    HOLD = 2

@dataclasses.dataclass
class Event:
    name: str
    _type: Events
    pos: tuple[int, int]

def print_event(event):
    print(f'state :> {event.name}\ntype :> {event._type}\npos :> {event.pos}')

class State:
    time_threashold = 0.25
    def __init__(self, name):
        self.name = name
        self._state = Events._NONE
        self.pos = (0, 0)
        self.time = None

    @property
    def state(self):
        return (Events._NONE, Events.CLICK)[mouse.is_pressed(self.name)]

    def _Click(self):
        if self._state != self.state == Events.CLICK:
            self.time = time.time()
            self._state = self.state
            self.pos = mouse.get_position()

    def _None(self):
        event = None
        if self._state == Events.CLICK and self.state == Events._NONE:
            if self.time:
                if time.time() - self.time < self.time_threashold:
                    event = Event(self.name, Events.CLICK, self.pos)
            self._state = Events._NONE
            self.time = None
            self.pos = (0, 0)
        return event

    def _Hold(self):
        if self.state == Events.CLICK and (self._state == Events.HOLD or self._state == Events.CLICK):
            cur = mouse.get_position()
            pos_delta = (cur[0] - self.pos[0], cur[1] - self.pos[1])
            event = Event(self.name, Events.HOLD, pos_delta)
            self.pos = cur
            return event
        elif self._state == self.state == Events.CLICK:
            if self.time:
                if time.time() - self.time > self.time_threashold:
                    self.time = None
                    self._state = Events.HOLD
                    cur = mouse.get_position()
                    pos_delta = (cur[0] - self.pos[0], cur[1] - self.pos[1])
                    event = Event(self.name, Events.HOLD, pos_delta)
                    self.pos = cur
                    return event


    def handle(self):
        temp = self._Hold()
        if temp is None:
            temp = self._Click()
            if temp is None:
                temp = self._None()
        return temp

class MouseHandle:
    def __init__(self):
        self.states = State('left'), State('right')
        self.events = []
        self.thread = None
        
    def listen(self):
        for ele in self.states:
            got = ele.handle()
            if got is not None:
                self.events.append(got)

    def on_mouse_event(self, event):
        if isinstance(event, (mouse.ButtonEvent, mouse.WheelEvent, mouse.MoveEvent)):
            self.listen()
            
    def start(self):
        mouse.hook(self.on_mouse_event)
        self.thread = threading.Thread(target=mouse.wait)
        self.thread.deamon = True
        self.thread.start()
        
if __name__ == '__main__':
    mhandle = MouseHandle()
    mhandle.start()
    while True:
        if mhandle.events:
            print_event(mhandle.events.pop(0))
            
