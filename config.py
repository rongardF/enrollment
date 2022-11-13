import os

class Config(object):
    SECRET_KY = os.environ.get("SECRET_KEY") or "secret_string" # this string is hashed and used to attach to a file (cooe, session etc.) to make sur eit is un-aletered by abd actors