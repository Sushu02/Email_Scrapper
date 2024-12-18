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

# AWS S3 Configuration from .env file
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
S3_FOLDER_NAME = os.getenv("S3_FOLDER_NAME")

# Connect to Email Inbox
def connect_to_email():
    print("Connecting to Gmail...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    print("Login successful.")
    return mail

# Get Yesterday's Date in Format 'DD-Mon-YYYY'
def get_yesterdays_date():
    yesterday = datetime.now() - timedelta(1)
    return yesterday.strftime("%d-%b-%Y")

# Fetch Emails from Yesterday
def fetch_yesterdays_emails(mail, folder="INBOX"):
    mail.select(folder)
    yesterday_date = get_yesterdays_date()
    print("Yesterday daye :- ", yesterday_date)
    # Search for emails received yesterday
    status, messages = mail.search(None, f'(SINCE "{yesterday_date}")')
    email_ids = messages[0].split()

    email_data = []
    for eid in email_ids:
        res, msg = mail.fetch(eid, "(RFC822)")
        for response_part in msg:
            if isinstance(response_part, tuple):
                raw_email = response_part[1]
                msg = email.message_from_bytes(raw_email)

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
    print("Complete data :- ", email_data)            
    return email_data

# Save Email Data to S3
def save_to_s3(data, s3_client):
    print("Saving to S3...")
    for email_info in data:
        # Use sender's email or name for the filename
        sender = email_info.get("from", "unknown_sender")
        sanitized_sender = sender.replace(" ", "_").replace("@", "_at_").replace("<", "").replace(">", "")
        filename = f"{S3_FOLDER_NAME}/emails/{sanitized_sender}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

        # Upload JSON data to S3
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=filename,
            Body=json.dumps(email_info, indent=4),
            ContentType="application/json"
        )
        print(f"Uploaded email from {sender} to S3 as {filename}")
# Main Function
def main():
    # Connect to the email inbox
    mail = connect_to_email()

    # Fetch yesterday's email data
    email_data = fetch_yesterdays_emails(mail)  # Fetch emails from yesterday

    # Connect to S3
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    # Save to S3 bucket
    save_to_s3(email_data, s3_client)

    # Close the email connection
    mail.logout()

if __name__ == "__main__":
    main()
