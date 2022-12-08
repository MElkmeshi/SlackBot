import slack
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import gspread

SLACK_TOKEN="xoxb-4383534212147-4484567459536-1MF3jZrYrhB4TBu3BlQnvwwi"
SIGNING_SECRET="0fc19ff12fbab88b02d6f7fb0a6b2236"

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SIGNING_SECRET,'/slack/events',app)
sa = gspread.service_account(filename="elzibda-slack-bot.json")
sh = sa.open("Slack Bot Messages")
whs = sh.worksheet("Elzibda")

client  = slack.WebClient(SLACK_TOKEN)
BOT_ID = client.api_call("auth.test")['user_id']

message_counts = {}

@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if BOT_ID != user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1
        client.chat_postMessage(channel=channel_id,text=text)

@app.route('/')
def home():
    return "Hello World!"


@app.route('/message-count',methods=['POST'])
def message_count():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    message_count = message_counts.get(user_id,0)
    msg = whs.acell('B2').value
    client.chat_postMessage(channel=channel_id,text=msg + str(message_count))
    return Response(), 200

@app.route('/Welcome',methods=['POST'])
def Welcome():
    data = request.form
    channel_id = data.get('channel_id')
    msg = whs.acell('B3').value
    client.chat_postMessage(channel=channel_id,text=msg)
    return Response(), 200

if __name__ == "__main__":
    app.run()
