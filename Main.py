import sys
from Vault import *
from json import loads, dumps

docs  =  'Args:\t\tCommand:\t\tDescription:'
docs +=  '--p\t\tpasskey\t\tThe key that is used to access the vault'

class ParsedCMD(dict):
	translate = {
		'p': 'passkey',
		's': 'set',
		'o': 'object',
		'g': 'get',
		'r': 'remove',
		'?': 'help',
		'h': 'help'
		}
	
	@classmethod
	def read(cls, *args):
		temp = cls({})
		for arg in ' '.join([arg for arg in args]).split('--'):
			for key in cls.translate.keys():
				if arg.startswith(key):
					temp[cls.translate[key]] = arg.split(' ')[1] if key != 'o' else arg[arg.index(' '):]
					continue
		temp, error = cls.validate(temp)
		assert temp, f'{error}'
		return temp
	
	@staticmethod
	def validate(_this):
		if 'help' in _this.keys():
			return False, docs
		if 'passkey' not in _this.keys():
			return False, 'the mandatory --passkey argument is missing'
		if [com in _this.keys() for com in ('get', 'set', 'remove')].count(True) > 1:
			return False, 'only one of the functions, get, set, remove at a time'
		if ['set' in _this.keys(), 'object' in _this.keys()].count(True) == 1:
			return False, 'the arguments set and object require each other'
		if 'object' in _this.keys():
			_this['object'] = _this['object'].strip().replace('{', '{"').replace('}', '"}').replace(',', '","').replace(':', '":"')
			try:
				_this['object'] = loads(_this['object'])
			except:
				return False, f'the object argument {_this["object"]} could not be jsonified'
		return _this, None


def main(*args):
	assert len(args) > 1, 'not enough args'
	temp = ParsedCMD.read(*args[1:])
	if temp.get('passkey', False):
		storage = getSecStorage(temp.get('passkey'))
		if len(temp.keys()) == 1:
			storage.create({})
			return f'Vault obj was created'
		else:
			if temp.get('get', False):
				return storage.get_key(temp.get('get'))
			elif temp.get('remove', False):
				storage.remove_key(temp.get('remove'))
				return f'removed {temp.get("remove")}'
			elif temp.get('set', False) and temp.get('object', False):
				storage.set_key(temp.get('set'), temp.get('object'))
				return f'{temp.get("set")} was set'
	return 'Something went Wrong'


# Execution Sandbox
if __name__ == '__main__':
	sys.stdout.write(f'{main(*sys.argv)}')
