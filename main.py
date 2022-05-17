from config import *
from flask import Flask, render_template, request, url_for, redirect, session
import tweepy
import json
from flask_session import Session

app = Flask(__name__)
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, callback=callback)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def update_count(filepath:str):
	with open(filepath, 'r+') as j:
		data = json.load(j)
		data["count"] += 1
		j.seek(0)
		json.dump(data, j)
		j.truncate()
		j.close()

@app.route('/')
def index():
	if session.get('oauth_verifier'):
		if session['oauth_verifier']:
			return render_template('index.html', goto='home', page_name='Home')
	return render_template('index.html', goto='login', page_name='Log in')

@app.route('/login')
def login():
	if session.get('oauth_verifier'):
		if session['oauth_verifier']:
			return redirect(url_for('home'))

	authorize_url = auth.get_authorization_url()
	return render_template('login.html', authorize_url=authorize_url)

@app.route('/callback')
def callback():
	oauth_token = request.args.get('oauth_token')
	oauth_verifier = request.args.get('oauth_verifier')

	session["oauth_verifier"] = oauth_verifier
	auth.get_access_token(oauth_verifier)

	return redirect(url_for('home'))

@app.route('/home')
def home():
	api = tweepy.API(auth)

	screen_name = api.verify_credentials().screen_name
	followers_count = api.verify_credentials().followers_count
	friends_count = api.verify_credentials().friends_count
	statuses_count = api.verify_credentials().statuses_count
	name = api.verify_credentials().name
	pp_url = api.verify_credentials().profile_image_url
	
	user = api.get_user(screen_name=screen_name)
	join_date = user.created_at

	return render_template('home.html',
							screen_name=screen_name, 
							followers_count=followers_count, 
							friends_count=friends_count, 
							statuses_count=statuses_count, 
							name=name,
							pp_url=pp_url,
							join_date=join_date)


@app.route('/tweet', methods=['GET', 'POST'])
def tweet():
	api = tweepy.API(auth)

	screen_name = api.verify_credentials().screen_name
	username = api.verify_credentials().name

	form_data = request.form.get('tweet-form')
	if form_data == None:
		pass
	else:
		api.update_status(form_data)
		update_count('data/tweet.json')
	
	return render_template('tweet.html',
							screen_name=screen_name,
							name=username)

@app.route('/logout')
def logout():
	session['oauth_verifier'] = None
	return redirect('/')

@app.route('/keep-alive')
def keep_alive():
	return "Ready!"


@app.errorhandler(500)
def internal_server_error(e):
	return render_template('error.html'), 500

if __name__ == '__main__':
	app.run(debug=True, port=port)
