import os
import base64
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import json
from tasks.utils import is_important_email

# Scopes required for Gmail API
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URI = os.getenv("TOKEN_URI")

def fetch_emails(access_token, refresh_token, last_updated=None):
    logging.debug("Fetching emails using provided access token.")

    # Create credentials from the access token
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri=TOKEN_URI
    )

    # Build the Gmail API client
    service = build("gmail", "v1", credentials=creds)

    days_ago = 3

    # Determine the threshold for fetching emails
    if last_updated:
        try:
            last_updated_dt = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        except ValueError:
            logging.warning("Unable to parse last_updated: %s. Defaulting to 3 days ago.", last_updated)
            last_updated_dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    else:
        last_updated_dt = None

    three_days_ago = datetime.now(timezone.utc) - timedelta(days=days_ago)
    if last_updated_dt:
        effective_dt = max(last_updated_dt, three_days_ago)
    else:
        effective_dt = three_days_ago

    effective_timestamp = int(effective_dt.timestamp())
    logging.debug("Fetching emails after timestamp: %d", effective_timestamp)

    # Use Gmail API to search for emails from the past day
    try:
        results = service.users().messages().list(
            userId="me",
            q=f"after:{effective_timestamp} in:inbox"
        ).execute()

        messages = results.get("messages", [])
        if not messages:
            logging.info("No emails found.")
            return []

        emails = []
        for msg in messages:
            # logging.debug("Processing message with id: %s", msg["id"])
            # Fetch email details
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            
            # Extract relevant details
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            date_str = next((h["value"] for h in headers if h["name"] == "Date"), None)
            size = int(msg_data.get("sizeEstimate", 0))
            # logging.debug("Email details - Subject: %s, From: %s, Date: %s, Size: %d", subject, sender, date_str if date_str else "None", size)

            # Parse the email date
            email_time = datetime.now(timezone.utc)
            if date_str:
                try:
                    email_time = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
                except ValueError:
                    logging.warning("Unable to parse date: %s, defaulting to current time", date_str)

            # Decode the body (if available)
            body = ""
            if "parts" in msg_data.get("payload", {}):
                for part in msg_data["payload"]["parts"]:
                    if part.get("mimeType") == "text/plain":
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                        # logging.debug("Decoded email body for message id: %s", msg["id"])
                        break

            logging.info("SENDER: %s", sender)
            # Append to the email list
            emails.append({
                "subject": subject,
                "from": sender,
                "date": email_time,
                "size": size,
                "body": body,
            })

        logging.info("Fetched %d emails.", len(emails))
        important_emails = [email for email in emails if is_important_email(email["subject"], email["body"], sender=email["from"])]
        unimportant_emails = [email for email in emails if not is_important_email(email["subject"], email["body"], sender=email["from"])]
        logging.info("Important emails (%d):", len(important_emails))
        for email in unimportant_emails:
            logging.info("Unimportant Email: %s", json.dumps(email["body"]))
        for email in important_emails:
            logging.info("Important Email: %s", json.dumps(email["body"]))
        return important_emails

    except HttpError as e:
        if e.resp.status == 401:
            logging.error("Unauthorized: Invalid access token.")
            return {"error": "Unauthorized", "status": 401}
        else:
            logging.error("An error occurred while fetching emails: %s", str(e))
            return []
    except Exception as e:
        logging.error("An error occurred while fetching emails: %s", str(e))
        return []

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    # Set your access token here (replace with actual token)
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    if not ACCESS_TOKEN:
        logging.error("Please set the ACCESS_TOKEN environment variable.")
    else:
        logging.info("Access token found; fetching emails.")
        emails = fetch_emails(ACCESS_TOKEN)
        logging.info("Processing %d emails in main block.", len(emails))
        for email_data in emails:
            logging.info("Email => Subject: %s | From: %s | Size: %d bytes", email_data['subject'], email_data['from'], email_data['size'])
