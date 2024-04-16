'''from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import imaplib
import email
from email.header import decode_header
import requests
import google.generativeai as genai
import os
import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown
from dotenv import load_dotenv
import os

genai.configure(api_key="AIzaSyDuyeP_WTzAPn0-f8i5TgD8xoCwbRiBlIY")
GEMINI_API_KEY="AIzaSyDuyeP_WTzAPn0-f8i5TgD8xoCwbRiBlIY"
#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-pro")

app = Flask(__name__)
#api_key = "AIzaSyDuyeP_WTzAPn0-f8i5TgD8xoCwbRiBlIY"
#GEMINI_API_KEY = "AIzaSyDuyeP_WTzAPn0-f8i5TgD8xoCwbRiBlIY"
# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")
db = client["email_data"]
collection = db["users"]


class Email:
    def __init__(self, email_body):
        self.email_body = email_body
    
    def retrieve_email_body(self):
        return self.email_body

def summarize_text_geminiai(text, api_key):
    #endpoint = "https://api.gemini.ai/v1/summarize"
    chat=model.start_chat()
    while True:
        message=input('You:')
        response=chat.send_message(message)
        print("Gemini  :"+response.text)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "text": text,
        "ratio": 0.3,  # Adjust the summary length ratio as needed
    }

    response = requests.post(endpoint, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["summary"]
    else:
        return None


def summarize_and_identify_action_items(email_body):
    chat = model.start_chat()
    
    # Send the email body as input to the AI model
    response = chat.send_message(email_body)
    
    # Get the summary generated by the AI model
    summary = response.text
    
    # Implement logic to identify action items like schedules and deadlines
    action_items = identify_action_items(summary)
    
    return summary, action_items

def identify_action_items(text):
    # Implement your logic to identify action items such as schedules and deadlines in the text
    # This could involve using regular expressions or natural language processing techniques
    
    # Placeholder implementation, assuming there are no action items
    action_items = []
    
    return action_items





def fetch_emails(username, password, GEMINI_API_KEY):
    # Connect to Gmail's IMAP server
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(username, password)
    imap.select("inbox")

    # Search for unread emails
    result, data = imap.search(None, "UNSEEN")
    email_ids = data[0].split()

    # Fetch email bodies for each unread email
    for email_id in email_ids:
        result, data = imap.fetch(email_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Get subject
        subject_header = msg["Subject"]
        subject = decode_header(subject_header)[0][0]
        subject = subject.decode() if isinstance(subject, bytes) else subject

        # Get sender
        from_header = msg.get("From")
        from_ = decode_header(from_header)[0][0]
        from_ = from_.decode() if isinstance(from_, bytes) else from_

        # Initialize the body variable
        body = ""

        # Extract body from MIME message
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode()
                    break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode()

        # Summarize email body using Gemini AI API
        summarized_body = summarize_and_identify_action_items(body)

        # Save email to MongoDB
        email_data = {
            "subject": subject,
            "from": from_,
            "body": summarized_body,
            "unread": True,
        }
        collection.insert_one(email_data)

        # Mark email as read
        imap.store(email_id, "+FLAGS", "\\Seen")

    # Close the connection
    imap.close()
    imap.logout()


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/submit", methods=["POST"])
def submit():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Store email and password in MongoDB
        user_data = {"email": email, "password": password}
        collection.insert_one(user_data)

        # Fetch emails
        fetch_emails(email, password,GEMINI_API_KEY) 

        return redirect(url_for("dashboard"))
    else:
        # Return a 405 Method Not Allowed error for other request methods
        return "Method Not Allowed", 405



@app.route("/dashboard")
def dashboard():
    # Fetch only unread emails from MongoDB
    unread_emails = collection.find({"unread": True})

    # Prepare a list to hold emails with summarized bodies
    emails_with_summaries = []

    # Iterate through unread emails
    for email in unread_emails:
        # Get the subject and sender from the email
        subject = email["subject"]
        sender = email["from"]

        # Get the body and summarize it using Gemini AI API
        body = email["body"]
        summarized_body = summarize_and_identify_action_items(body)

        # Append the email with summarized body to the list
        emails_with_summaries.append({"subject": subject, "from": sender, "summarized_body": summarized_body})

    # Render the dashboard template with the emails data
    return render_template("dashboard.html", emails=emails_with_summaries)



if __name__ == "__main__":
    app.run(debug=True)
'''
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import imaplib
import email
from email.header import decode_header
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")
db = client["email_data"]
collection = db["emails"]

# Initialize Flask app
app = Flask(__name__)

# Define Email class
class Email:
    def __init__(self, email_body):
        self.email_body = email_body
    
    def retrieve_email_body(self):
        return self.email_body

def summarize_and_identify_action_items(email_body):
    # Start a chat with the Generative AI model
    chat = genai.GenerativeModel("gemini-pro").start_chat()
    
    # Send the email body as input to the AI model
    response = chat.send_message(email_body)
    
    # Get the summary generated by the AI model
    summary = response.text
    
    # Implement logic to identify action items like schedules and deadlines
    action_items = []  # Placeholder, implement your logic here
    
    return summary, action_items

def fetch_emails(username, password):
    # Connect to Gmail's IMAP server
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(username, password)
    imap.select("inbox")

    # Search for unread emails
    result, data = imap.search(None, "UNSEEN")
    email_ids = data[0].split()

    # Fetch email bodies for each unread email
    for email_id in email_ids:
        result, data = imap.fetch(email_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Extract email body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

        # Summarize email body using Gemini AI API
        summary, action_items = summarize_and_identify_action_items(body)

        # Save email to MongoDB
        email_data = {
            "subject": msg["Subject"],
            "from": msg["From"],
            "body": summary,
            "unread": True,
        }
        collection.insert_one(email_data)

        # Mark email as read
        imap.store(email_id, "+FLAGS", "\\Seen")

    # Close the connection
    imap.close()
    imap.logout()

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/submit", methods=["POST"])
def submit():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Fetch emails
        fetch_emails(email, password)

        return redirect(url_for("dashboard"))
    else:
        return "Method Not Allowed", 405

@app.route("/dashboard")
def dashboard():
    # Fetch only unread emails from MongoDB
    unread_emails = collection.find({"unread": True})

    # Prepare a list to hold emails with summarized bodies
    emails_with_summaries = []

    # Iterate through unread emails
    for email in unread_emails:
        # Get the subject and sender from the email
        subject = email["subject"]
        sender = email["from"]

        # Get the body and summarize it using Gemini AI API
        body = email["body"]
        summarized_body = summarize_and_identify_action_items(body)

        # Append the email with summarized body to the list
        emails_with_summaries.append({"subject": subject, "from": sender, "summarized_body": summarized_body})

    # Render the dashboard template with the emails data
    return render_template("dashboard.html", emails=emails_with_summaries)

if __name__ == "__main__":
    app.run(debug=True)