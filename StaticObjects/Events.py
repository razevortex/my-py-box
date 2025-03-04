from dataclasses import dataclass


@dataclass(frozen=True)
class Events:
    name = ''
    
    def __eq__(self, other):
        other = other if not isinstance(other, Events) else other.name
        return self.name == other

    def __str__(self):
        return self.name


class Hover(Events):
    name = 'hover'


class Click(Events):
    name = 'click'


class Drag(Events):
    name = 'drag'


class Release(Events):
    name = 'release'


class No(Events):
    name = 'none'


class Press(Events):
    name = 'press'


class Hold(Events):
    name = 'hold'
    
    
class InputStateIO:
    _state = (Events(), Events())
    _action = (Events(), Events())
    __slots__ = 'state', 'name'
    
    def __init__(self, name):
        self.name = name
        self.state = self._state[0]
    
    def update_status(self):
        self._update_status()
    
    def _update_status(self, got=None):
        for state, action in zip(self._state, self._action):
            if action == got and self.state not in (state, action):
                self.state = action
                return
            elif self.state == action:
                self.state = state
                return

if __name__ == '__main__':
	pass
