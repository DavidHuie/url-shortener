"""
A very simple URL shortener service
By: David Huie

Usage: This service takes in a url via POST and returns a JSON-encoded response
       with a relative URL that leads to the original URL.

       $ python app/app.py &
       $ curl --data-urlencode 'url=gmail.com' localhost:5000/shorten
       {"url": "/url/db50d"}

       You'll now be redirected to the original url by pointing your browser to
       localhost:5000/url/db40d.
"""
import json
import redis
import sha

from flask import abort
from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask import url_for

db = redis.StrictRedis(host='localhost', port=6666, db=0)
app = Flask(__name__)

@app.route('/shorten', methods=['POST'])
def shorten_url():
	"""This shortens a URL included in the POST response."""

	# Let's not accept invalid url values
	if 'url' not in request.form or not request.form['url']:
		response = app.make_response(json.dumps({'error': 'Invalid url.'}))
		response.status = '403 Invalid url'
		response.mimetype = 'text/json'

		return response

	url = request.form['url']

	# Correct invalid URLs (very simple)
	if not url.startswith('http'):
		url = 'http://%s' % url

	# Keep only the first 5 characters of the sha value
	shortened_url = sha.sha(url).hexdigest()[:5]

	# Record the mapping in our DB
	_record_url(shortened_url, url)

	response = app.make_response(json.dumps({'url': url_for('get_url', shortened_url=shortened_url)}))
	response.mimetype = 'text/json'

	return response

PREFIX = 'SHORTENED_'
def _record_url(shortened_url, url):
	"""Records a shortened_url -> url mapping in our DB."""
	db.set(PREFIX + shortened_url, url)

@app.route('/url/<shortened_url>', methods=['GET'])
def get_url(shortened_url):
	"""Handles a URL containing a shortened url by redirecting
	to the site specified by shortened_url in the DB."""
	destination = db.get(PREFIX + shortened_url)

	if not destination:
		return abort(404)

	return redirect(destination)

if __name__ == '__main__':
	app.run()
