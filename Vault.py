from CryptString import CryStr
from BitFile import BitString
from json import dumps, loads
from dataclasses import dataclass
import os, sys
from os import path as Path


def getSecStorage(crypt_key):
	crypt_key = CryStr(crypt_key)
	
	@dataclass(frozen=True)
	class SecStorage:
		crypt_key:CryStr
		file_path:Path
	
		def create(self, data: dict | type(None)) -> None:
			BitString.i2b(*[ord(char) for char in self.crypt_key.encrypt(dumps(data))], _N=8).write(self.file_path)
	
		def get_data(self) -> dict:
			assert Path.exists(self.file_path), f'{self.file_path} seems not to exist'
			return loads(self.crypt_key.decrypt(''.join([chr(val) for val in BitString.read(self.file_path).b2i(_N=8)])))
		
		def get_key(self, key) -> dict:
			return self.get_data().get(key, None)
		
		def remove_key(self, key):
			self.create({_key: val for _key, val in self.get_data().items() if _key != key})
			
		def set_key(self, key:str, data:dict):
			temp = self.get_data()
			if not temp.get(key, False):
				temp[key] = data
			self.create(temp)
	
	return SecStorage(crypt_key, Path.join(Path.dirname(Path.abspath(sys.argv[0])), crypt_key._hash + '.bin'))
	

if __name__ == '__main__':
	pass
