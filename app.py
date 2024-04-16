from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import imaplib
import email
from email.header import decode_header
import requests

app = Flask(__name__)

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")
db = client["email_data"]
collection = db["users"]
class Email:
    def __init__(self, email_body):
        self.email_body = email_body
    
    def retrieve_email_body(self):
        return self.email_body
'''
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
        

        # Extract body from multipart message
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Find plain text email body
                if "attachment" not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode()
                    break
        else:
            # Extract body from non-multipart message
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode()

        # Summarize email body
        summarized_body = summarize_text_geminiai(body)
        if summarized_body is None:
            summarized_body = "Summary not available"
        # Instantiate Email class with email body
        email_instance = Email(body)
        retrieved_body = email_instance.retrieve_email_body()



  
        # Save email to MongoDB
        email_data = {
            "subject": subject,
            "from": from_,
            "body": retrieved_body,
            "unread": True,
        }
        collection.insert_one(email_data)

        # Mark email as read
        imap.store(email_id, "+FLAGS", "\\Seen")

'''
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

        # Save email to MongoDB
        email_data = {
            "subject": subject,
            "from": from_,
            "body": body,
            "unread": True,
        }
        collection.insert_one(email_data)

        # Mark email as read
        imap.store(email_id, "+FLAGS", "\\Seen")

    # Close the connection
    imap.close()
    imap.logout()

# Function to summarize text using Gemini AI
'''
def summarize_text_geminiai(text):
    api_key = "AIzaSyDuyeP_WTzAPn0-f8i5TgD8xoCwbRiBlIY"
    endpoint = "https://api.gemini.ai/v1/summarize"

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

'''
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
        fetch_emails(email, password)

        return redirect(url_for("dashboard"))
    else:
        # Return a 405 Method Not Allowed error for other request methods
        return "Method Not Allowed", 405


@app.route("/dashboard")
def dashboard():
    # Fetch only unread emails from MongoDB
    unread_emails = collection.find({"unread": True})
    return render_template("dashboard.html", emails=unread_emails)


if __name__ == "__main__":
    app.run(debug=True)
