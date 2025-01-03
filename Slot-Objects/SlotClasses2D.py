class Slot2D:
    __name__ = '2DSlot'
    __slots__ = ()

    def __init__(self, *args):
        for i, arg in enumerate(args):
            if i < len(self.__slots__):
                self.__setattr__(self.__slots__[i], self.Slot_(*arg))

    @property
    def Slot_(self):
        slots = tuple([f'{s}' for s in self.__slots__])
        class SB(SlotBase):
            __slots__ = slots
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
        return SB

    @property
    def keys(self):
        keys = []
        [[keys.append(f'{key}:{k}') for k in self.__slots__] for key in self.__slots__]
        return (key for key in keys)
        
    def __iter__(self):
        return (self.__getattribute__(slot) for slot in self.__slots__)

    def __dict__(self):
        return {key: self.__getitem__(key) for key in self.keys}

    def __list__(self):
        return [val for val in self.__dict__().values()]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return all([a == b for a, b in zip(self.__list__(), other.__list__())])

    def __getitem__(self, item):
        return self.__getattribute__(item.split(':')[0]).__getattribute__(item.split(':')[1])

    def __setitem__(self, item, val):
        self.__getattribute__(item.split(':')[0]).__setattr__(item.split(':')[1], val)
