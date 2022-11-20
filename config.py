import os

class Config(object):
    # os.environ provides a way to access user defined variables in the shell (process) where Python was started 
    # syntax: if left-hand argument is not None, then that will be assigned; if None then right-side argument will be assigned
    SECRET_KEY = os.environ.get("SECRET_KEY") or b'\\\x8e\xf4\xd1\xa8\xfa\x08\xea\xf1\xaa\xb0\xc9\x10\r"\x96' # this string is hashed and used to attach to a file (cookie, session etc.) to make sure it is un-altered by bad actors
    
    MONGODB_SETTINGS={ 'db' : 'UTA_Enrollment' }
    