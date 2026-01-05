import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from gmail_auth import gmail_authenticate

def send_email(to_email, subject, body):
    creds = gmail_authenticate()
    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(body)
    message["to"] = to_email
    message["subject"] = subject

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    send_body = {"raw": encoded_message}

    service.users().messages().send(
        userId="me",
        body=send_body
    ).execute()
