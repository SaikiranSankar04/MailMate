from simplegmail import Gmail
from datetime import datetime, timedelta
from pymongo import MongoClient
from email.header import decode_header
import google.generativeai as genai
from dotenv import load_dotenv
import os
import nltk
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag


# Configure Gemini API
genai.configure(api_key="AIzaSyDuyeP_WTzAPn0-f8i5TgD8xoCwbRiBlIY")


gmail = Gmail()  # will open a browser window to ask you to log in and authenticate


# Get all messages in the inbox

params = {
    "to": "saikiranshankar.2004@gmail.com",
    "sender": "saikiranshankar.2004@gmail.com",
    "subject": "My first email",
    "msg_html": "<h1>Woah, my first email!</h1><br />This is an HTML email.",
    "msg_plain": "Hi\nThis is a plain text email.",
    "signature": True,  # use my account signature
}
"""
message = gmail.send_message(
    **params
)  # equivalent to send_message(to="you@youremail.com", sender=...)
"""
yesterday = (datetime.now() - timedelta(1)).strftime("%Y/%m/%d")

# Construct the query
query = f'in:inbox is:unread after:{yesterday} before:{(datetime.now()).strftime("%Y/%m/%d")}'

# Fetch unread messages from yesterday in the inbox
messages = gmail.get_messages(query=query)
"""
# Print them out
for message in messages:
    print("To: " + message.recipient)
    print("From: " + message.sender)
    print("Subject: " + message.subject)
    print("Date: " + message.date)
    print("Preview: " + message.snippet)

    # Check if the plain text body is None and handle it
    if message.plain:
        print("Message Body: " + message.plain)
    else:
        print("Message Body: No plain text content")
"""

# Connect to MongoDB
client = MongoClient(
    "mongodb://localhost:27017/"
)  # Replace with your MongoDB connection string
db = client["email_db"]  # Create/use a database named 'email_db'
collection = db["emails"]  # Create/use a collection named 'emails'

# Prepare the emails for insertion
emails_to_insert = []
for message in messages:
    email_data = {
        "to": message.recipient,
        "from": message.sender,
        "subject": message.subject,
        "date": message.date,
        "snippet": message.snippet,
        "body": message.plain if message.plain else "No plain text content",
        "message_id": message.id,  # Add message_id to uniquely identify the email
    }

    # Check if the email already exists in the collection
    if not collection.find_one({"message_id": message.id}):
        emails_to_insert.append(email_data)

# Insert the emails into the collection
if emails_to_insert:
    collection.insert_many(emails_to_insert)


# Confirm insertion
print(f"Inserted {len(emails_to_insert)} emails into the database.")

# Close the MongoDB connection
client.close()
