from flask import Flask, request
import requests
import json

app = Flask(__name__)

FBAPI_TOKEN = "EAAIQpPZCH35ABAAGjLihZAOm3yVcXjDH7mjM6u06pgNbBnZAdLh18lryJ9NN1SidsTjAG0zl2iRy1gigKwSc400Q9hE5GV88YfCLC7t84RFuNNVOjVeAdHNJFcpodkNZBqekdNZC08cfg2Te4XeHwxk6heSR5dKPq7M5aiVxInAZDZD"
VERIFY_TOKEN = "topsecret"
MM_TOKEN = "5927ab827d8781120cc4779f67e043cd"

FB_URL = "https://graph.facebook.com/v2.6/me/messages?access_token=" + FBAPI_TOKEN
MM_URL = "https://api.musixmatch.com/ws/1.1/track.search"

SUCCESS = 200
DESCENDING = "DESC"
FAILURE_MSG = "Something went wrong! :("
NORESULTS_MSG = "No results found! :("
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
		's_track_rating' : DESCENDING,
		's_artist_rating' : DESCENDING,
		'format' : 'json' }
	resp=requests.get(MM_URL,params=params)
	song_info = resp.json()
	if song_info['message']['header']['status_code'] != 200:
	 	return FAILURE_MSG
	if song_info['message']['header']['available'] == 0:
		return NORESULTS_MSG
	msg = "Track: " + song_info['message']['body']['track_list'][0]['track']['track_name'] 
	msg += "\nAlbum: " + song_info['message']['body']['track_list'][0]['track']['album_name']
	msg += "\nArtist: " + song_info['message']['body']['track_list'][0]['track']['artist_name']
	lyrics_url = song_info['message']['body']['track_list'][0]['track']['track_share_url']
	data = {"info":msg , "lyrics_url":lyrics_url}
	return data

def send_msg(user_id,message,lyrics_url):
    data = {
        "recipient": {"id": user_id},
        "message": {
        	"attachment":{
        		"type": "template",
	        	"payload":{
					"template_type":"button",
					"text":message,
					"buttons":[
						{
							"type":"web_url",
							"url":lyrics_url,
							"title": SHOW_LYRICS
						}
	        		]
	        	}
        	}
        }
    }
    resp = requests.post(FB_URL, json=data)

@app.route('/', methods=['POST'])
def handle_incoming_messages():
	data = request.json
	sender_id = data['entry'][0]['messaging'][0]['sender']['id']
	song = data['entry'][0]['messaging'][0]['message']['text']
	track_info = get_song_info(song)
	send_msg(sender_id,track_info['info'],track_info['lyrics_url'])
	return "ok"

if __name__ == '__main__':
    app.run(debug=True)