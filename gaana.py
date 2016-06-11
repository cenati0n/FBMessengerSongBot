from flask import Flask, request
import requests

app = Flask(__name__)

FBAPI_TOKEN = "EAAIQpPZCH35ABAAGjLihZAOm3yVcXjDH7mjM6u06pgNbBnZAdLh18lryJ9NN1SidsTjAG0zl2iRy1gigKwSc400Q9hE5GV88YfCLC7t84RFuNNVOjVeAdHNJFcpodkNZBqekdNZC08cfg2Te4XeHwxk6heSR5dKPq7M5aiVxInAZDZD"
VERIFY_TOKEN = "topsecret"

FB_URL = "https://graph.facebook.com/v2.6/me/messages?access_token=" + FBAPI_TOKEN

@app.route('/', methods=['GET'])
def handle_verification():
	if request.args['hub.verify_token'] == VERIFY_TOKEN:
		return request.args['hub.challenge']
	else:
		return "Verification Failed!"

def send_msg(user_id,message):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": message}
    }
    resp = requests.post(FB_URL, json=data)
    print(resp.url)

@app.route('/', methods=['POST'])
def handle_incoming_messages():
	data = request.json
	sender_id = data['entry'][0]['messaging'][0]['sender']['id']
	message = data['entry'][0]['messaging'][0]['message']['text']
	send_msg(sender_id,message)
	return "ok"

if __name__ == '__main__':
    app.run(debug=True)