from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
import pyotp
import os
import base64
import hashlib


class CryptoFile(str):

	@property
	def _hash(self):
		hash_ = self
		for _ in range(len(self)):
			hash_ = hashlib.sha256(hash_.encode()).hexdigest()
		return hash_[-len(self):] + hash_[:-len(self)]
	
	@property
	def pw(self):
		return self.encode('utf-8')
	

class PWCrypt(CryptoFile):
	
	@classmethod
	def auto_gen(cls, leng0th=16):
		from random import randint as rng
		symbols = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*',
		           '+', ',', '-', '.', '/', '0', '1', '2', '3', '4',
		           '5', '6', '7', '8', '9', ':', ';', '<', '=', '>',
		           '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
		           'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
		           'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b',
		           'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
		           'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
		           'w', 'x', 'y', 'z']
		return cls(''.join([symbols[rng(0, len(symbols) - 1)] for _ in range(length)]))

	def get_key(self, salt):
		return PBKDF2(self.pw, salt, dkLen=32, count=100000, hmac_hash_module=SHA256)
	
	def encrypt(self, data: str | bytes) -> bytes:
		data_bytes = data if isinstance(data, bytes) else data.encode('utf-8')
		salt, iv = os.urandom(16), os.urandom(16)
		cipher = AES.new(self.get_key(salt), AES.MODE_CBC, iv)
		ciphertext = cipher.encrypt(pad(data_bytes, AES.block_size))
		return base64.b64encode(salt + iv + ciphertext)
	
	def decrypt(self, encrypted_data:bytes) -> bytes:
		if isinstance(encrypted_data, str):
			encrypted_data = base64.b64decode(encrypted_data)
		cipher = AES.new(self.get_key(encrypted_data[:16]), AES.MODE_CBC, encrypted_data[16:32])
		return unpad(cipher.decrypt(encrypted_data[32:]), AES.block_size)
	
	
class MFACrypt(PWCrypt):
	
	@classmethod
	def auto_gen(cls, *args, **kwargs):
		from ToolBox.QR import QRC
		user = input('enter for which username:')
		secret = pyotp.random_base32()
		QRC(data=pyotp.TOTP(secret).provisioning_uri(name=user, issuer_name=cls.__name__)).export_img()
		print(f'KEY:{secret}')
		return cls(secret)
	
	def get_key(self, salt):
		if pyotp.TOTP(self).verify(input('Enter MFA:')):
			return super().get_key(salt)
	

if __name__ == '__main__':
	test = PWCrypt.auto_gen()
	data = test.encrypt('hello world')
	print(data)
	print(test.decrypt(data))
	