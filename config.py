import os

consumer_key=os.environ.get("consumer_key")
consumer_secret=os.environ.get("consumer_secret")
callback=os.environ.get("callback")
port=os.environ.get("port", 5000)
isdebug=os.environ.get("isdebug", False)
