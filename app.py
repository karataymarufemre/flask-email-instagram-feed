from flask import Flask
from flask import request
from flask_cors import CORS
import smtplib
import os
from email.mime.text import MIMEText
from typing import NamedTuple
import requests
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler


load_dotenv()
class Media(NamedTuple):
    caption: str
    id: str

media_urls = []


sender_address = os.getenv('SENDER_ADDRESS')
sender_pass = os.getenv('SENDER_PASS')

access_token = os.getenv('ACCESS_TOKEN')
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/mail', methods=['GET', 'POST'])
def welcome():
    if request.method == 'POST':
        print(request.json)
        mail_content = "Email adress: " + request.json["address"] +  "\nName: " + request.json["name"] + "\n\n" + request.json["content"]
        #Setup the MIME
        message = MIMEText(mail_content)
        message['From'] = sender_address
        message['To'] = sender_address
        message['Subject'] = 'Website Contact Form! from: ' +  request.json["address"]  #The subject line
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, sender_address, text)
        session.quit()
        return {}


@app.route('/new_access_token', methods=['GET', 'POST'])
def generate_new_access_token():
    global access_token
    response = requests.get("https://graph.instagram.com/refresh_access_token", params={"grant_type": "ig_refresh_token", "access_token": access_token} )
    json = response.json()
    access_token = json["access_token"]
    return []

@app.route('/instagram_batch', methods=['GET', 'POST'])
def instagram_get_media_batch():
    media_ids = get_media_ids()
    global media_urls
    media_urls = []
    for i in media_ids:
        media_id = i["id"]
        caption = i["caption"]
        if media_id is None or caption is None:
            continue
        try:
            response = requests.get("https://graph.instagram.com/" + media_id, params={"fields": "media_url", "access_token": access_token} )
            json = response.json()
            if json["media_url"] is None:
                continue
            media_urls.append({"url": json["media_url"], "caption": caption})
        except:
            continue
    return []

@app.route('/instagram_urls', methods=['GET', 'POST'])
def instagram_get_image_urls():
    return media_urls

@app.route("/")
def hello():
    return "Hello world!"

def get_media_ids():
    media_ids = []
    response = requests.get("https://graph.instagram.com/me/media", params={"fields": "id,caption,media_url,media_type,children", "access_token": access_token} )
    json = response.json()
    for x in json["data"]:
        if x["media_type"] == "IMAGE":
            media_ids.append({"id": x["id"], "caption":x["caption"]})
        if x["media_type"] == "CAROUSEL_ALBUM":
            for i in x["children"]["data"]:
                media_ids.append({"id": i["id"], "caption":x["caption"]})
    print(media_ids)
    print("meida id printed")
    return media_ids
if __name__ == '__main__':
    app.run()