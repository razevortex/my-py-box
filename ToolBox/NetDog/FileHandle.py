from pathlib import Path
from json import dumps, loads
from datetime import datetime as dt

root = Path(__file__).absolute()


class Config:
	_config = Path('/'.join(root.parts[:-1]) + '/data/watchlist.config')
	_log = Path('/'.join(root.parts[:-1]) + '/data/status.log')

	def __init__(self):
		super().__init__()
	
	def update_log(self, **kwargs):
		temp = self.log_obj
		for key, val in kwargs.items():
			temp[key] = val
		f = open(self._log, 'w')
		f.write(dumps(temp, indent=4))
		f.close()
			
	@property
	def log_obj(self):
		f = open(self._log, 'r')
		temp = loads(f.read())
		f.close()
		return temp
	
	@staticmethod
	def valid_line(line):
		if line.startswith('#'):
			return False
		elif any([item == '' for item in line.split(',')]):
			return False
		else:
			return True
		
	@property
	def conf_lines(self):
		f = open(self._config, 'r')
		arr = [line for line in f.read().split('\n') if self.valid_line(line)]
		f.close()
		return arr
	
	@property
	def conf_header(self):
		return [key for key in self.conf_lines[0].split(',')]
	
	def loaded(self):
		arr = []
		log = self.log_obj
		for line in self.conf_lines[1:]:
			
			temp = {}
			for key, val in zip(self.conf_header, line.split(',')):
			
				temp[key] = val if key not in ['laziness', 'log_size', 'frequency'] else int(val)
			temp.update(log.get(temp['name'], {'logs': [], 'lazy_counter': 0}))
			arr.append(temp)
		print(f'loaded: {arr}')
		return arr


class ErrorLog:
	_err = Path(''.join(root.parts[:-1]) + '/data/watchlist.config')
	
	def __init__(self):
		if not self._err.exists():
			with open(self._err, 'w') as f:
				f.write('')
		
	@property
	def timestamp(self):
		return dt.now().strftime('%d.%m.%Y %H:%M:%S')
	
	def write(self, err):
		with open(self._err, 'a') as f:
			f.write(f'\n{self.timestamp}:\t{err}')

	
if __name__ == '__main__':
	pass
