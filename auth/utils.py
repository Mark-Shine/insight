import os
from hashlib import sha256,md5
from hmac import HMAC
from base64 import b64encode, b64decode

def encrypt_password(password, salt=None):
    """Hash password on the fly."""
    if salt is None:
        salt = os.urandom(8) # 64 bits.

    assert 8 == len(salt)
    assert isinstance(salt, str)

    if isinstance(password, unicode):
        password = password.encode('UTF-8')

    assert isinstance(password, str)

    result = password
    for i in xrange(10):
        result = HMAC(result, salt, sha256).digest()

    return b64encode(salt + result)

def validate_password(hashed, input_password):
    _hashed = b64decode(hashed)
    return hashed == encrypt_password(input_password, salt=_hashed[:8])


if __name__ == '__main__':
    hashed = encrypt_password("hello world") 
    assert validate_password(hashed, "hello world")
    print hashed