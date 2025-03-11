import os
import base64
import hashlib
from pathlib import Path
from json import dumps, loads
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad


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

    def KEY(self, salt=None, iv=None):
        salt, iv = [os.urandom(16) if key is None else key for key in [salt, iv]]
        return PBKDF2(self.pw, salt, dkLen=32, count=100000, hmac_hash_module=SHA256), salt, iv

    def encrypt(self, data):
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
            return_str = True
        else:
            data_bytes = data
            return_str = False

        key, salt, iv = self.KEY()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(data_bytes, AES.block_size))
        encrypted = salt + iv + ciphertext
        return base64.b64encode(encrypted).decode('utf-8') if return_str else encrypted


    def decrypt(self, encrypted_data):
        
        if isinstance(encrypted_data, str):
            encrypted_data = base64.b64decode(encrypted_data)

        # Extract components
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]
        key, _, __ = self.KEY(salt=salt, iv=iv)
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return decrypted


class KeyVault:
    key_class = EncryptedString
    root_path = Path('V:\\vault')

    @classmethod
    def setVaultPath(cls, here:Path):
        assert here.is_dir(), 'the path must be a dir'
        cls.root_path = here
        
    @classmethod
    def store(cls, key, data:dict):
        cryp = cls.key_class(key)
        data = cryp.encrypt(dumps(data))
        write = False
        if (cls.root_path / f'{cryp._hash}.json').exists():
            write = 'Y' == input('key already exists override enter "Y":')
        else:
            write = True
        if write:
            with open(cls.root_path / f'{cryp._hash}.json', 'w') as f:
                f.write(data)

    @classmethod
    def load(cls, key):
        cryp = cls.key_class(key)
        if (cls.root_path / f'{cryp._hash}.json').exists():
            with open(cls.root_path / f'{cryp._hash}.json', 'r') as f:
                return loads(cryp.decrypt(f.read()))


class KeyEntry:
    @classmethod
    def create(cls):
        temp = {}
        temp['at'] = input('secret used at:')
        temp['as'] = input('secret used as:')
        temp['key'] = input('secret key:')
        return input('vault key:'), temp
        
if __name__ == '__main__':
    got = None
    while got != 'exit':
        got = input('store, load or exit?')
        if got == 'store':
            KeyVault.store(*KeyEntry.create())
        elif got == 'load':
            print(KeyVault.load(input('enter vault key:')))
        elif got == 'exit':
            break
        else:
            pass

