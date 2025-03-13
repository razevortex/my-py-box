from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from random import randint as rng
import os
import base64
import hashlib


class EncryptedString(str):

    @property
    def _hash(self):
        hash_ = self
        for _ in range(len(self)):
            hash_ = hashlib.sha256(hash_.encode()).hexdigest()
        return hash_

    @property
    def pw(self):
        return self.encode('utf-8')

    def encrypt(self, data):
        """
        Encrypts data using the string instance as password.

        Args:
            data (str|bytes): Data to encrypt

        Returns:
            bytes|str: Encrypted data in bytes (if input was bytes)
                      or base64 string (if input was str)
        """
        # Convert string input to bytes

        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
            return_str = True
        else:
            data_bytes = data
            return_str = False

        # Generate random salt and IV
        salt = os.urandom(16)
        iv = os.urandom(16)

        # Derive encryption key
        key = PBKDF2(
            self.pw,
            salt,
            dkLen=32,
            count=100000,  # PBKDF2 iterations
            hmac_hash_module=SHA256
        )

        # Encrypt data
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(data_bytes, AES.block_size))

        # Combine salt + IV + ciphertext
        encrypted = salt + iv + ciphertext

        return base64.b64encode(encrypted).decode('utf-8') if return_str else encrypted

    def decrypt(self, encrypted_data):
        """
        Decrypts data using the string instance as password.

        Args:
            encrypted_data (str|bytes): Data to decrypt

        Returns:
            bytes: Decrypted bytes (call .decode() to get string)
        """
        # Convert base64 string to bytes
        if isinstance(encrypted_data, str):
            encrypted_data = base64.b64decode(encrypted_data)

        # Extract components
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]

        # Derive encryption key
        key = PBKDF2(
            self.pw,
            salt,
            dkLen=32,
            count=100000,
            hmac_hash_module=SHA256
        )

        # Decrypt data
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)

        return decrypted.decode('utf-8')


class KeyVaultRng(dict):
	
	def __new__(cls, **kwargs):
		cls.CryPyObj = EncryptedString(''.join([f'{rng(0, 9)}' for _ in range(16)]))
		return super().__new__(cls)
	
	def store_new(self, key, val:str):
		self.__setitem__(key, self.CryPyObj.encrypt(val))
		
	def __getitem__(self, key):
		return self.CryPyObj.decrypt(super().__getitem__(key))


class KeyVault(KeyVaultRng):
	
	def __new__(cls, passcode, **kwargs):
		cls.CryPyObj = EncryptedString(passcode)
		return super().__new__(cls)
