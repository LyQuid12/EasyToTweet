import requests
from bs4 import BeautifulSoup
import json
import os
from config import *

def check_update(filepath:str=os.getcwd()+'/data/tweet.json'):
    gist = 'https://gist.github.com/LyQuid12/'+gist_id
    html = requests.get(gist).text
    soup = BeautifulSoup(html, 'html.parser')
    raw_button = soup.find_all('div', class_='file-actions flex-order-2 pt-0')
    raw_url = f"https://gist.github.com/{raw_button[0].contents[1].attrs['href'][1:]}"
    raw_data = requests.get(raw_url).json()["count"]
    
    with open(filepath, 'r') as tw:
        data = json.load(tw)["count"]

    if data <= raw_data-1:
        tw.close()
        with open(filepath, 'r+') as count:
            count_data = json.load(count)
            count_data["count"] = raw_data
            count.seek(0)
            json.dump(count_data, count)
            count.truncate()
            count.close()
            return True
    else:
        tw.close()
        return False

def update_gist(filepath:str=os.getcwd()+'/data/tweet.json'):
	content=open(filepath, 'r').read()
	headers = {'Authorization': f'token {gist_token}'}
	r = requests.patch('https://api.github.com/gists/' + gist_id, data=json.dumps({'files':{filename:{"content":content}}}),headers=headers) 

def update_count(filepath:str=os.getcwd()+'/data/tweet.json'):
	with open(filepath, 'r+') as j:
		data = json.load(j)
		data["count"] += 1
		j.seek(0)
		json.dump(data, j)
		j.truncate()
		j.close()
