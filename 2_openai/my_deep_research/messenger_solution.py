from dotenv import load_dotenv
import os
from email.message import EmailMessage
import smtplib
from agents import function_tool
import requests

load_dotenv(override=True)

### Send Email Function ###

# Email constants
EMAIL_ADDRESS       = os.getenv("EMAIL_ADDRESS")
EMAIL_SMTP_SERVER   = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_APP_PASSWORD  = os.getenv("EMAIL_APP_PASSWORD")

# create a message object of the EmailMessage object
msg1 = EmailMessage()

# Define send_email function
def send_email(subject: str, text_body: str, html_body: str):
    # Create a message object from EmailMessage() class
    msg = EmailMessage()
    
    msg["From"] = EMAIL_ADDRESS
    msg["To"]   = EMAIL_ADDRESS
    msg["Subject"] = subject
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(EMAIL_SMTP_SERVER, 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg)


### Push Function ###

# pushover constants
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

# push function definition
def push(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)


### Send Message Function ###
USE_EMAIL = True

def send_message(subject, text_body, html_body):
    if USE_EMAIL:
        send_email(subject, text_body, html_body)
    else:
        push(f"Subject: {subject}\n\n{text_body}")

### send email tool ###
@function_tool
def send_email_tool(subject: str, text_body: str, html_body: str) -> str:
    """
    Send out an email with given subject and text_body to all the sales prospects.
    
    Args:
    subject: subject of the email.
    text_body: body of the email in plain text.
    html_body: body of the email in html format.
    """
    send_message(subject, text_body, html_body)
    return "Email sent succesfully"