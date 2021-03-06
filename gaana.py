from flask import Flask, request
from pprint import pprint
import requests
import json

app = Flask(__name__)

FBAPI_TOKEN = "EAAIQpPZCH35ABAO5TTIl9eyvvgoqkPPLXmICRigJkZBtVc2nLUwmbrptM1MMhcczlW3zBDl1igfM2Mdkdab2Jf9o9hzQ8wZBwRALxSml4UCmBELcy57jyk6S4svWJmZB9j4azt555ECszG65k6ZBMEVj8ci8M8i5uxUwZASaVXZAQZDZD"
VERIFY_TOKEN = "topsecret"
MM_TOKEN = "5927ab827d8781120cc4779f67e043cd"

FB_URL = "https://graph.facebook.com/v2.6/me/messages?access_token=" + FBAPI_TOKEN
MM_URL = "https://api.musixmatch.com/ws/1.1/track.search"

SUCCESS = 200
DESCENDING = "DESC"
FAILURE_MSG = "Something went wrong! :("
NORESULTS_MSG = "No results found! :("
INVALID_MSG = "Please send text message"
SHOW_LYRICS = "Show Lyrics\t\t\t\t\t\t"

@app.route('/', methods=['GET'])
def handle_verification():
	if request.args['hub.verify_token'] == VERIFY_TOKEN:
		return request.args['hub.challenge']
	else:
		return "Verification Failed!"

def get_song_info(song):
	params = {
		'apikey' : MM_TOKEN, 
		'q_lyrics' : song ,
		'f_has_lyrics':1,
		'format' : 'json' }
	resp=requests.get(MM_URL,params=params)
	song_info = resp.json()
	data = {}
	data['status_code'] = song_info['message']['header']['status_code'] 
	data['size'] = song_info['message']['header']['available']
	data['track_list'] = []
	item = {}
	count = 1
	if song_info['message']['header']['status_code'] == 200:
		for i in song_info['message']['body']['track_list']:
			if count > 5:
				break;
			item['track'] = "Track: " + i['track']['track_name'] 
			item['album'] = "Album: " + i['track']['album_name']
			item['artist'] = "Artist: " + i['track']['artist_name']
			item['lyrics_url'] = i['track']['track_share_url']
			item['image_url'] = i['track']['album_coverart_500x500']
			data['track_list'].append(item.copy())
			#print item
			count += 1
	#pprint(data)
	return data

def send_error_msg(sender_id):
	data = {}
	data['recipient'] = {'id': sender_id}
	data['message'] = {'text':INVALID_MSG}
	resp = requests.post(FB_URL, json=data)

def send_msg(msg):
	data = {}
	data['recipient'] = {'id': msg['sender_id']}
	if msg['status_code'] != 200:
		data['message'] = {'text':FAILURE_MSG}
	elif msg['size'] == 0:
		data['message'] = {'text':NORESULTS_MSG}
	else:
		data['message'] = {}
		data['message']['attachment'] = {}
		data['message']['attachment']['type']='template'
		data['message']['attachment']['payload'] = {}
		data['message']['attachment']['payload']['template_type']='generic'
		data['message']['attachment']['payload']['elements']=[]
		item={}
		for i in msg['track_list']:
			item['title']=i['track']
			item['image_url']=i['image_url']
			item['subtitle']=i['album'] + '\n' + i['artist']
			item['buttons']=[
				{
					"type":"web_url",
					"url" : i['lyrics_url'],
					"title": SHOW_LYRICS 
				}
			]

			data['message']['attachment']['payload']['elements'].append(item.copy())
	#pprint(data)
	resp = requests.post(FB_URL, json=data)

@app.route('/', methods=['POST'])
def handle_incoming_messages():
	data = request.json
	sender_id = data['entry'][0]['messaging'][0]['sender']['id']
	if 'text' in data['entry'][0]['messaging'][0]['message']:
		song = data['entry'][0]['messaging'][0]['message']['text'].encode('unicode_escape')
		msg = get_song_info(song)
		msg["sender_id"] = sender_id
		send_msg(msg)
	else:
		send_error_msg(sender_id)
	return "ok"

if __name__ == '__main__':
    app.run(debug=True)