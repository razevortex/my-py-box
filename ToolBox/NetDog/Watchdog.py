from MailBot import *
from FileHandle import *
from DataHandler import *


class Watchdog:
    __slots__ = 'name', 'laziness', 'log_size', 'Log', 'Message', 'comparison'
    
    def __init__(self, **kwargs):
        self.comparison = {key: value for key, value in kwargs.items() if key != 'logs'}
        for slot in ('name', 'laziness', 'log_size'):
            self.__setattr__(slot, kwargs[slot])
        self.Log = Log(**kwargs)
        self.Message = Message(**kwargs)

    @property
    def msg_keys(self):
        return {'ip': self.Log.ip, 'name': self.name, 'log': self.Log[-1].__str__(), 'state': str(self.Log[-1].state)}
    
    def run(self):
        if self.Log.get_ping():
            if self.Log.trigger_report(self.laziness):
                MailBot('wjwautomail@gmail.com', 'ongpiynuwiwefcvz').send(*self.Message.build(**self.msg_keys))
                return True
            return False


class Container(list):
    def __init__(self, update_timer=120):
        self.update_timer = TimerInterval(update_timer)
        self.kill_switch = []
        super().__init__([Watchdog(**item) for item in Config().loaded()])
    
    @property
    def name_list(self):
        return [item.name for item in self]

    def remove_(self, items):
        names = [item.get('name', '') for item in items]
        for name in self.name_list:
            if name not in names:
                self.pop(self.name_list.index(name))

    def _update(self):
        temp = {}
        for item in self:
            temp.update({item.name: item.Log.export(item.log_size)})
        print('write to logs: ', temp)
        Config().update_log(**temp)
        self.remove_(Config().loaded())
        for item in Config().loaded():
            if item.get('name') in self.name_list:
                comp = {key: val for key, val in item.items() if key != 'logs'}
                if self[self.name_list.index(item.get('name'))].comparison != comp:
                    try:
                        self[self.name_list.index(item.get('name'))] = Watchdog(**item)
                    except:
                        ErrorLog().write(f'updating {str(item)} failed')
            else:
                try:
                    self.append(Watchdog(**item))
                except:
                    ErrorLog().write(f'creating {str(item)} failed')
    
    @property
    def trigger_kill_switch(self):
        if len(self.kill_switch) > 2 * len(self):
            self.kill_switch = self.kill_switch[-(2 * len(self)):]
        return self.kill_switch.count(True) > len(self)
    
    def run(self):
        while not self.trigger_kill_switch:
            if self.update_timer.ready:
                print('update')
                self._update()
            for item in self:
                try:
                    if not (temp := item.run()) is None:
                        self.kill_switch.append(temp)
                except:
                    pass

           
if __name__ == '__main__':
    test = Container(update_timer=20)
    test.run()

    '''def test_probe():
        arr = []
        testprobe = Probe('8.8.8.8', 3)
        while len(arr) < 2:
            got = testprobe.ping()
            if not got is None:
                arr.append(got)
        for item in arr:
            print(item)

    test_probe()'''

    # Example usage:
    #ip = "8.8.8.8"  # Google's public DNS server
    #test = sp.run(['ping', '-n', '1', '8.8.8.8'], stdout=sp.PIPE, encoding="ISO-8859-1")
    #print(test.stdout.decode('cp1252'))
    #result = sp.check_output(["ping", "-n", "1", "192.20.20.8"]).decode("ISO-8859-1")
    #print(test)
    #temp = re.search(r"Zeit=(\d+)ms", result)
    #print(temp.group(1))
    