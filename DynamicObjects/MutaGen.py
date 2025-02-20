from SlotObjects.Verticies import *
from SlotObjects.Pixel import *

class MuValGen:
    __slots__ = '_gen', 'last_event', 'event_dict'
    
    def __init__(self, default, **kwargs):
        self.event_dict = {None: default}
        self.event_dict.update(kwargs)
        self.last_event = None
        self._gen = self._create_generator(self.get_static_gen(self.event_dict.get(self.last_event)))
    
    def add_event(self, key, value):
        assert isinstance(value[0], type(self.event_dict.get(None)[0])), 'type error'
        self.event_dict[key] = value
    
    def get_static_gen(self, value: tuple):
        value, _ = value
        def gen(value):
            while True:
                yield value
        return gen(value)
    
    def set_dynamic_gen(self):
        start = self.current
        end, steps = self.event_dict.get(self.last_event)
        step = (end - start) / steps
        def new_gen(start, end, steps, step):
            steps -= 1
            while steps > 0:
                start += step
                yield start
                steps -= 1
            yield end
        self._gen = self._create_generator(original_gen=new_gen(start, end, steps, step))
    
    def get_event(self, event=None):
        if self.last_event != event:
            self.last_event = event
            if self.event_dict.get(self.last_event, False):
                self.set_dynamic_gen()
    
    def _create_generator(self, original_gen=None, value=None):
        assert original_gen is not None or value is not None, 'Either original_gen or value must be provided'
        if original_gen is None:
            while True:
                yield value
        else:
            last_value = None
            exhausted = False
        while True:
            if not exhausted:
                try:
                    last_value = next(original_gen)
                except StopIteration:
                    exhausted = True
                    if last_value is None:
                        return  # Raise StopIteration if no elements were generated
                else:
                    yield last_value
            else:
                yield last_value
    
    @property
    def current(self):
        return next(self._gen)
        

class MuCircleGen:
    __slots__ = '_center', '_radius', '_color'
    
    def __init__(self, rel_center, rel_radius, color, frames=30):
        '''
        rel_center: Vertex
        rel_radius: Vertex
        color: Pixel
        frames: int
        '''
        self._center = MuValGen((rel_center, frames))
        self._radius = MuValGen((rel_radius, frames))
        self._color = MuValGen((color, frames))
        
if __name__ == '__main__':
    test = MuValGen((Pixel4(0, 0, 0, 0), 30), hover=(Pixel4(0, 0, 0, 255), 40), click=(Pixel4(255, 0, 0, 255), 10))
    for i in range(30):
        if i == 2:
            test.get_event('hover')
        if i == 20:
            test.get_event('click')
        print(test.current.__tuple__())
        
