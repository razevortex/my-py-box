from dataclasses import dataclass as dacla

@dacla(frozen=True)
class repr_helper:
    tabs = ['|', ':', '=']
    pad = ' '
    breakout = 25

    def next_tab(self, strings):
        _dict = {}
        for tab in self.tabs:
            
            if all([tab in s for s in strings]):
                _dict[tab] = [s.index(tab) for s in strings]
        k, i = None, None
        for key, val in _dict.items():
            if i is None or min(val) < min(i):
                k, i = key, val
        return k, i

    def condition(self, strings):
        for tab in self.tabs:
            if all([tab in s for s in strings]):
                return True
        return False

    def align(self, string, prefix='', suffix='\n'):
        if not isinstance(string, list):
            strings = [s.strip() for s in string.split('\n')]
        else:
            strings = string
        output = ['' for _ in range(len(strings))]
        breakout_i = 0
        while self.condition(strings):
            breakout_i += 1
            if breakout_i > self.breakout:
                break
            tab, indicies = self.next_tab(strings)
            assert not indicies is None, 'No tabs found'
            for i in range(len(strings)):
                temp, strings[i] = strings[i][:indicies[i]] + self.pad * (max(indicies) - indicies[i]) + tab,  strings[i][indicies[i]+1:]
                output[i] += temp
        return ''.join([f'{prefix}{s}{suffix}' for s in output])
            

