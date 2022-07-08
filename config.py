import os

consumer_key=os.environ.get("consumer_key")
consumer_secret=os.environ.get("consumer_secret")
callback=os.environ.get("callback")
gist_token=os.environ.get("gist_token")
gist_id=os.environ.get("gist_id")
site_key=os.environ.get("site_key")
key_secret=os.environ.get("key_secret")
port=os.environ.get("port", 8000)
isdebug=False