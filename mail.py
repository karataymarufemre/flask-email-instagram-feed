from flask import Flask
from flask import request
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


sender_address = 'marufemre99@gmail.com'
sender_pass = 'dzkmypyatuduzrgx'

app = Flask(__name__)
@app.route('/mail', methods=['GET', 'POST'])
def welcome():
    if request.method == 'POST':
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
        return "ok"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)