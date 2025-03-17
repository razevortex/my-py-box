from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
import os
import base64
import hashlib


class CryStr(str):
	
	@property
	def _hash(self):
		hash_ = self
		for _ in range(len(self)):
			hash_ = hashlib.sha256(hash_.encode()).hexdigest()
		return hash_[-len(self):] + hash_[:-len(self)]
	
	@property
	def pw(self):
		return self.encode('utf-8')
	
	def get_key(self, salt):
		return PBKDF2(self.pw, salt, dkLen=32, count=100000, hmac_hash_module=SHA256)
	
	def encrypt(self, data: str):
		data_bytes = data.encode('utf-8')
		salt, iv = os.urandom(16), os.urandom(16)
		cipher = AES.new(self.get_key(salt), AES.MODE_CBC, iv)
		ciphertext = cipher.encrypt(pad(data_bytes, AES.block_size))
		return base64.b64encode(salt + iv + ciphertext).decode('utf-8')
	
	def decrypt(self, encrypted_data):
		if isinstance(encrypted_data, str):
			encrypted_data = base64.b64decode(encrypted_data)
		cipher = AES.new(self.get_key(encrypted_data[:16]), AES.MODE_CBC, encrypted_data[16:32])
		decrypted = unpad(cipher.decrypt(encrypted_data[32:]), AES.block_size)
		return decrypted.decode('utf-8')


if __name__ == '__main__':
	temp = CryStr('245ertf')
	got = temp.encrypt('lol was los')
	print(got)
	print(temp.decrypt(got))
