import os
import base64
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Scopes required for Gmail API
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URI = os.getenv("TOKEN_URI")

def fetch_emails(access_token):
    print("Fetching emails using access token...")

    # Create credentials from the access token
    creds = Credentials(
        token=access_token,
        # refresh_token=refresh_token,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri=TOKEN_URI
    )

    # Build the Gmail API client
    service = build("gmail", "v1", credentials=creds)

    # Calculate the date for filtering emails from the past day
    one_day_ago = int((datetime.now(timezone.utc) - timedelta(days=1)).timestamp())

    # Use Gmail API to search for emails from the past day
    try:
        results = service.users().messages().list(
            userId="me",
            q=f"after:{one_day_ago}"
        ).execute()

        messages = results.get("messages", [])
        if not messages:
            print("No emails found.")
            return []

        emails = []
        for msg in messages:
            # Fetch email details
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            
            # Extract relevant details
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            date_str = next((h["value"] for h in headers if h["name"] == "Date"), None)
            size = int(msg_data.get("sizeEstimate", 0))

            # Parse the email date
            email_time = datetime.now(timezone.utc)
            if date_str:
                try:
                    email_time = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
                except ValueError:
                    pass  # If parsing fails, default to now

            # Decode the body (if available)
            body = ""
            if "parts" in msg_data.get("payload", {}):
                for part in msg_data["payload"]["parts"]:
                    if part.get("mimeType") == "text/plain":
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                        break

            # Append to the email list
            emails.append({
                "subject": subject,
                "from": sender,
                "date": email_time,
                "size": size,
                "body": body,
            })

        print(f"Fetched {len(emails)} emails.")
        return emails

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example usage
if __name__ == "__main__":
    # Set your access token here (replace with actual token)
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    if not ACCESS_TOKEN:
        print("Please set the ACCESS_TOKEN environment variable.")
    else:
        emails = fetch_emails_with_token(ACCESS_TOKEN)
        for email_data in emails:
            print(f"Subject: {email_data['subject']}")
            print(f"From: {email_data['from']}")
            print(f"Size: {email_data['size']} bytes")
            print("-" * 50)
