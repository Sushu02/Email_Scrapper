import boto3
import imaplib
import email
from email.header import decode_header
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Email Configuration from .env file
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
IMAP_SERVER = os.getenv("IMAP_SERVER")

# Connect to Email Inbox
def connect_to_email():
    print("Entered to Gmail")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    print("Login Successfull")
    return mail

# Get Yesterday's Date in Format 'DD-Mon-YYYY'
def get_yesterdays_date():
    print("Get Yesterdays date")
    yesterday = datetime.now() - timedelta(1)
    print("Yeserdays date :", yesterday)
    return yesterday.strftime("%d-%b-%Y")

# Fetch Emails from Yesterday
def fetch_yesterdays_emails(mail, folder="INBOX"):
    print("Fetch the inbox for yesterday")
    mail.select(folder)
    yesterday_date = get_yesterdays_date()

    # Search for emails received yesterday
    status, messages = mail.search(None, f'(SINCE "{yesterday_date}")')
    email_ids = messages[0].split()
    print("Email_ids", email_ids)
    email_data = []
    print("Email data", email_data)
    
    for eid in email_ids:
        res, msg = mail.fetch(eid, "(RFC822)")
        for response_part in msg:
            if isinstance(response_part, tuple):
                raw_email = response_part[1]
                msg = email.message_from_bytes(raw_email)
                print("Message", msg)
                # Decode email metadata
                subject, encoding = decode_header(msg["Subject"])[0]
                subject = subject.decode(encoding) if isinstance(subject, bytes) else subject
                sender = msg.get("From")
                date = msg.get("Date")

                # Extract email body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()

                email_data.append({
                    "subject": subject,
                    "from": sender,
                    "date": date,
                    # "body": body
                })
    print("Complete data", email_data)
    return email_data

# Save to Local File
def save_to_local_file(data, file_name):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Saved {file_name} locally.")

# Main Function
def main():
    # Connect to the email inbox
    mail = connect_to_email()
    
    # Fetch yesterday's email data
    email_data = fetch_yesterdays_emails(mail)  # Fetch emails from yesterday
    
    # Save to local file
    file_name = "email_data_yesterday1.json"
    save_to_local_file(email_data, file_name)
    
    # Print the email data (for testing purposes)
    for email_info in email_data:
        print(email_info)
    
    # Close the connection
    mail.logout()

if __name__ == "__main__":
    main()
