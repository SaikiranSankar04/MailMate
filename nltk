import nltk
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag

# Sample text for analysis
text = """
We need to finalize the project proposal by Friday. 
Please review the document and provide your feedback by tomorrow.
Once approved, we'll proceed with the implementation phase. 
The meeting is scheduled for next Monday at 10:00 AM in Conference Room A.
"""

# Function to extract dates using regular expressions
def extract_dates(text):
    dates = re.findall(r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', text.lower())
    return dates

# Function to extract times using regular expressions
def extract_times(text):
    times = re.findall(r'\b(?:[0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]\s*(?:AM|PM|am|pm)?\b', text)
    return times

# Function to extract venue using regular expressions
def extract_venue(text):
    venues = re.findall(r'\bin\b\s+([^\.,\n]+)', text, re.IGNORECASE)
    return venues

# Tokenize the text into sentences
sentences = sent_tokenize(text)

# Initialize lists to store extracted information
action_items = []
dates = []
times = []
venues = []

# Define function to check if a word is a verb
def is_verb(tag):
    return tag.startswith('VB')

# Process each sentence to identify action items, dates, times, and venue
for sentence in sentences:
    # Tokenize the sentence into words
    words = word_tokenize(sentence)
    # Perform part-of-speech tagging
    tagged_words = pos_tag(words)
    # Extract verbs from tagged words as action items
    action_items.extend([word for word, tag in tagged_words if is_verb(tag)])
    # Extract dates from the sentence
    dates.extend(extract_dates(sentence))
    # Extract times from the sentence
    times.extend(extract_times(sentence))
    # Extract venue from the sentence
    venues.extend(extract_venue(sentence))

# Print extracted information
print("Action Items:")
for action_item in action_items:
    print("-", action_item)

print("\nDates:")
for date in dates:
    print("-", date)

print("\nTimes:")
for time in times:
    print("-", time)

print("\nVenue:")
for venue in venues:
    print("-", venue)
