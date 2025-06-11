from pathlib import Path
from dataclasses import dataclass
from datetime import datetime as dt, timedelta as td
import subprocess as sp
import re


class TimerInterval:
    __slots__ = 'interval', 'last_t'
    
    def __init__(self, interval: int):
        self.interval = td(seconds=interval)
        self.last_t = dt.now()
    
    @property
    def ready(self):

        if dt.now() - self.last_t >= self.interval:
            self.last_t = dt.now()
            return True
        else:
            return False


class Message(object):
    __slots__ = 'subject', 'body', 'report_to'
    
    def __init__(self, **kwargs):
        [self.__setattr__(slot, kwargs.get(slot)) for slot in self.__slots__]
    
    def build(self, **kwargs):
        temp = self.__str__()
        for key, val in kwargs.items():
            if f'*{key}*' in temp:
                temp = temp.replace(f'*{key}*', val)
        return self.report_to, temp
    
    def __str__(self):
        return f'Subject: {self.subject}\n\n{self.body}'


class Log(list):
    def __init__(self, **kwargs):
        arr = kwargs.get('logs', [])
        super().__init__([Entry(*a) for a in arr])
        self.probe = Probe(kwargs['ip'], kwargs['frequency'])
        self.lazy_counter = kwargs.get('lazy_counter', 0)
        self.last_state = None if len(self) < 1 else self[-1].state
        self.get_ping()
    
    def __repr__(self):
        return f'{self.ip} :\n\tstate: {self.last_state}\n\tcounter: {self.lazy_counter}\n\tlogs: {[item for item in self]}'
    
    @property
    def ip(self):
        return self.probe.ip

    def set_last_state(self, get):
        if not len(self) < 1 or self.last_state is None:
            self.append(get)
            self.last_state = self[-1].state
            self.lazy_counter = 0
        return None if len(self) < 1 else self[-1].state

    def get_ping(self):
        if (get := self.probe.ping()) is not None:
            if self.last_state is None:
                self.set_last_state(get)
                return
            else:
                if get.state != self.last_state:
                    print(f'state switch : {get.state} <> {self.last_state}')
                    self.set_last_state(get)
                else:
                    print(f'counter: {self.lazy_counter} => {self.lazy_counter +1}')
                    self.lazy_counter += 1
            return True
        return False
    
    def trigger_report(self, threshold):
        if self.lazy_counter > threshold:
            self.lazy_counter = threshold + 1
        return self.lazy_counter == threshold
        
    def export(self, size):
        temp = {'logs': [item.export for item in self], 'lazy_counter': self.lazy_counter}
        if len(temp) > size:
            temp['logs'] = temp['logs'][-size:]
        return temp
    

@dataclass
class Entry:
    _timestamp: str
    _state: int

    def __init__(self, timestamp, state: int):
        if isinstance(timestamp, dt):
            timestamp = timestamp.strftime('%d.%m.%Y %H:%M:%S')
        self._timestamp = timestamp
        self._state = state

    def __repr__(self):
        return f'{self._timestamp}: {self._state}ms'
    
    def __str__(self):
        return f'{self._timestamp} => {self.state}'
    
    @property
    def export(self):
        return [self._timestamp, self._state]
    
    @classmethod
    def now(cls, state: int):
        return cls(dt.now(), state)

    def __list__(self):
        return [self._timestamp, self._state]

    @property
    def state(self):
        return self._state > 0

    @property
    def timestamp(self):
        return dt.strptime(self._timestamp, '%d.%m.%Y %H:%M:%S')


class Probe(object):
    __slots__ = 'ip', 'timer'
    
    def __init__(self, ip: str, frequency: int):
        self.ip = ip
        self.timer = TimerInterval(frequency)
    
    @property
    def check_relay_network(self):
        response = sp.run(['ping', '-n', '1', '172.20.20.52'], stdout=sp.PIPE, encoding="ISO-8859-1")
        return response.returncode == 0
    
    def get_ping_response(self):
        response = sp.run(['ping', '-n', '1', self.ip], stdout=sp.PIPE, encoding="ISO-8859-1")
        if response.returncode == 0:
            return response.stdout
        else:
            return -1

    def resolve_ping(self):
        if (result := self.get_ping_response()) == -1:
            return Entry.now(-1)
        result = result.casefold()
        for lang in ('time', 'zeit'):
            if lang in result:
                for match in [re.search(lang + r"=(\d+)ms", result), re.search(lang + r"<(\d+)ms", result)]:
                    if match:
                        return Entry.now(int(match.group(1)))
                return Entry.now(-2)
        return False
    
    def ping(self) -> Entry | None:
        if self.timer.ready and self.check_relay_network:
            return self.resolve_ping()
        else:
            return None

        
if __name__ == '__main__':
    pass
