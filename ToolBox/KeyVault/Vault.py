from CryptString import CryStr
from BitFile import BitString
from json import dumps, loads
from dataclasses import dataclass
import os, sys
# Note that Path is not the Path from pathlib 
from os import path as Path


def getSecStorage(crypt_key:str):
	'''
 	crypt_key : str -> is the plain password
  	return the SecStorage class that can read/write/del objects from the Vault
  	'''
	crypt_key = CryStr(crypt_key)
	
	@dataclass(frozen=True)
	class SecStorage:
		crypt_key:CryStr
		file_path:Path
	
		def create(self, data: dict = dict()) -> None:
			'''
   			The stored data is a from a dict build json formated string.
	  		So this method dumps the dict -> str
	 		encrypts the string and builds a list of there int representation str -> list(int,int,...)
			converts each int to its 8bit binary and concatenates them list(int,int,...) -> bitarray
   			writes the bitarray to a file named like the _hash of the crypt_key + .bin
   			'''
			BitString.i2b(*[ord(char) for char in self.crypt_key.encrypt(dumps(data))], _N=8).write(self.file_path)
	
		def get_data(self) -> dict:
			assert Path.exists(self.file_path), f'{self.file_path} seems not to exist'
			return loads(self.crypt_key.decrypt(''.join([chr(val) for val in BitString.read(self.file_path).b2i(_N=8)])))
		
		def get_key(self, key) -> dict:
			return self.get_data().get(key, None)
		
		def remove_key(self, key) -> None:
			self.create({_key: val for _key, val in self.get_data().items() if _key != key})
			
		def set_key(self, key:str, data:dict) -> None:
			temp = self.get_data()
			if not temp.get(key, False):
				temp[key] = data
			self.create(temp)
	
	return SecStorage(crypt_key, Path.join(Path.dirname(Path.abspath(sys.argv[0])), crypt_key._hash + '.bin'))
	

if __name__ == '__main__':
	pass
