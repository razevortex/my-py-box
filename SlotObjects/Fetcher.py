class FetcherObject:
    __slots__ = 'getter', 'keys'
    def __init__(self, getter, keys=[]):
        self.getter = getter
        self.keys = keys

    def __getattribute__(self, key):
        if key in super().__getattribute__('keys'):
            return super().__getattribute__('getter').__getattribute__(key)
        else:
            return super().__getattribute__(key)


if __name__ == '__main__':
	pass
