from config import *
from flask import Flask, render_template, request, url_for, redirect, session
import tweepy
from flask_session import Session
from data.tweet import check_update, update_count, update_gist
from flask_hcaptcha import hCaptcha

app = Flask(__name__)
hcaptcha = hCaptcha(app=app, site_key=site_key, secret_key=secret_key, is_enabled=True)
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, callback=callback)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
	if session.get('oauth_verifier'):
		if session['oauth_verifier']:
			return render_template('index.html', goto='home', page_name='Home')
	return render_template('index.html', goto='login', page_name='Log in')

@app.route('/login', methods=["GET", "POST"])
def login():
	if session.get('oauth_verifier'):
		if session['oauth_verifier']:
			return redirect(url_for('home'))

	authorize_url = ""
	if request.method == "POST":
	    if hcaptcha.verify():
	        return redirect(auth.get_authorization_url())
	    else:
	        authorize_url = "/logout"
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
	try:
		api = tweepy.API(auth)

		screen_name = api.verify_credentials().screen_name
		followers_count = api.verify_credentials().followers_count
		friends_count = api.verify_credentials().friends_count
		statuses_count = api.verify_credentials().statuses_count
		name = api.verify_credentials().name
		pp_url = api.verify_credentials().profile_image_url

		user = api.get_user(screen_name=screen_name)
		join_date = user.created_at
		join_date = str(join_date)
		join_date = join_date.replace("-", "/")
		join_date = join_date.split("+")[0]

		return render_template('home.html',
								screen_name=screen_name, 
								followers_count=followers_count, 
								friends_count=friends_count, 
								statuses_count=statuses_count, 
								name=name,
								pp_url=pp_url,
								join_date=join_date)

	except tweepy.Forbidden:
		return redirect(url_for('logout'))


@app.route('/tweet', methods=['GET', 'POST'])
def tweet():
	try:
		api = tweepy.API(auth)

		screen_name = api.verify_credentials().screen_name

		form_data = request.form.get('tweet-form')
		if form_data == None:
			pass
		else:
			try:
				check_update()
				api.update_status(form_data)
				update_count()
				update_gist()
				alert_msg = "Tweet sent!"
				return render_template('tweet.html', screen_name=screen_name, alert_msg=alert_msg)
			except tweepy.TweepyException as TwExc:
				alert_msg = f"Error : {TwExc}"
				return render_template('tweet.html', screen_name=screen_name, alert_msg=alert_msg)

		return render_template('tweet.html', screen_name=screen_name, alert_msg="none")
	
	except tweepy.Forbidden:
		return redirect(url_for('logout'))

@app.route('/logout')
def logout():
	session['oauth_verifier'] = None
	return redirect('/')

@app.route('/keep-alive')
def keep_alive():
	return "Ready!"

##### Error handler #####

@app.errorhandler(404)
def error_page_not_found(e):
    return render_template('error.html'), 404

@app.errorhandler(403)
def error_forbidden(e):
	return render_template('error.html'), 403

@app.errorhandler(410)
def error_gone(e):
	return render_template('error.html'), 410

@app.errorhandler(500)
def error_internal_server_error(e):
	return render_template('error.html'), 500

if __name__ == '__main__':
	app.run(debug=isdebug, port=port)
