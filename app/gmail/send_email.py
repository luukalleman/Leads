import os
import base64
import re
import requests
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class GmailService:
    """
    A class to interact with the Gmail API for sending emails.
    """

    GMAIL_ACCESS_TOKEN_URL = "https://oauth2.googleapis.com/token"

    def __init__(self):
        self.client_id = os.getenv("GMAIL_CLIENT_ID")
        self.client_secret = os.getenv("GMAIL_CLIENT_SECRET")
        self.refresh_token = os.getenv("GMAIL_REFRESH_TOKEN")

    def get_access_token(self):
        """
        Retrieve the Gmail access token using the refresh token.
        """
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }
        response = requests.post(self.GMAIL_ACCESS_TOKEN_URL, data=payload)

        if response.status_code == 200:
            access_token = response.json().get("access_token")
            return access_token
        else:
            print(f"Failed to get access token: {response.json()}")
            return None

    def build_service(self, access_token):
        """
        Build the Gmail API service using the provided access token.
        """
        credentials = Credentials(access_token)
        service = build("gmail", "v1", credentials=credentials)
        return service

    @staticmethod
    def create_email_message(sender, recipient, subject, body):
        """
        Create an email message.
        """
        message = MIMEText(body, "html")  # Email body is treated as HTML
        message["to"] = recipient
        message["from"] = sender
        message["subject"] = subject

        # Encode the message in base64
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        return {"raw": encoded_message}

    @staticmethod
    def clean_email_content(content):
        """
        Removes unwanted characters or formatting artifacts from the email content,
        keeping only the HTML content.
        """
        # Use regex to extract content within the HTML code block
        match = re.search(r"```html(.*?)```", content, re.DOTALL)
        if match:
            return match.group(1).strip()  # Strip whitespace around the HTML content
        return content.strip()  # Fallback: Return stripped content

    def send_email(self, service, sender, recipient, subject, body):
        """
        Send an email using the Gmail API.
        """
        try:
            message = self.create_email_message(sender, recipient, subject, body)
            send_message = service.users().messages().send(userId="me", body=message).execute()
            return send_message
        except Exception as e:
            print(f"Failed to send email to {recipient}: {e}")
            return None

    def fetch_email_responses(self, service, sent_emails):
        """
        Fetch email responses for the given sent emails.

        Args:
            service: Gmail API service instance.
            sent_emails (list): List of dictionaries containing sent email details (e.g., thread ID, recipient).

        Returns:
            list: A list of email IDs that have received responses.
        """
        responded_emails = []
        for email in sent_emails:
            thread_id = email.get("thread_id")  # Assuming you store the thread ID in the database
            recipient_email = email.get("recipient_email")

            if not thread_id:
                continue

            try:
                thread = service.users().threads().get(userId="me", id=thread_id).execute()
                messages = thread.get("messages", [])

                for message in messages[1:]:  # Skip the first message (the sent email itself)
                    headers = {header["name"]: header["value"] for header in message["payload"]["headers"]}
                    if headers.get("From") == recipient_email:
                        print(f"Response detected for email to {recipient_email}")
                        responded_emails.append(email["id"])
                        break

            except Exception as e:
                print(f"Error fetching thread {thread_id}: {e}")

        return responded_emails
