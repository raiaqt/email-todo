import os
import imaplib
import email
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
import re

def fetch_emails(imap_server="imap.gmail.com"):
    print("Fetching emails...")

    username = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(username, password)
    mail.select("inbox")
    
    # Search for emails from the past 1 day
    date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%d-%b-%Y")
    result, data = mail.search(None, f'SINCE {date}')
    if result != "OK":
        raise Exception("Failed to search emails.")

    email_ids = data[0].split()
    total_emails = len(email_ids)
    if total_emails == 0:
        print("No emails found.")
        return []

    # Set size threshold (e.g., 50 KB)
    SIZE_THRESHOLD = 50000  # Adjust as needed (50 KB = 50,000 bytes)

    emails = []
    selected_emails_count = 0
    print("Selecting headers")
    for email_id in email_ids:
        # Fetch headers only
        result, header_data = mail.fetch(email_id, "(BODY.PEEK[HEADER] RFC822.SIZE)")
        if result != "OK":
            continue

        headers = None
        size = None

        for response_part in header_data:
            if isinstance(response_part, tuple):
                # Extract size using regex
                if b"RFC822.SIZE" in response_part[0]:
                    match = re.search(r"RFC822\.SIZE (\d+)", response_part[0].decode())
                    if match:
                        size = int(match.group(1))
                        if size > SIZE_THRESHOLD:
                            break  # Skip this email if it's too large
                
                # Extract email headers
                if response_part[1]:
                    headers = email.message_from_bytes(response_part[1])
        
        if headers is None or size is None or size > SIZE_THRESHOLD:
            continue  # Skip emails that don't meet criteria

        # Extract metadata from headers
        subject = headers["subject"] or "No Subject"
        sender = headers["from"] or "Unknown Sender"
        date_str = headers["Date"]

        # Parse the email date
        try:
            email_time = parsedate_to_datetime(date_str)  # Aware datetime
        except (TypeError, ValueError):
            continue  # Skip if the date is invalid

        # Ensure email_time is offset-aware
        if email_time.tzinfo is None:
            email_time = email_time.replace(tzinfo=timezone.utc)

        # Append metadata to the list
        emails.append({
            "id": email_id,
            "subject": subject,
            "from": sender,
            "date": email_time,
            "size": size,
        })
        selected_emails_count += 1

    print("Parsing emails")
    for email_meta in emails:
        # Fetch full content for the email
        result, msg_data = mail.fetch(email_meta["id"], "(BODY.PEEK[])")
        if result != "OK":
            continue

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                if msg.is_multipart():
                    body = ""
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            break  # Stop after the first plain text part
                else:
                    body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

                # Add the email body to the metadata
                email_meta["body"] = body

    mail.logout()
    print(f"Selected {selected_emails_count} of {total_emails} emails.")
    return emails

# Example usage
if __name__ == "__main__":
    fetched_emails = fetch_emails()
    for email_data in fetched_emails:
        print(f"Subject: {email_data['subject']}")
        print(f"From: {email_data['from']}")
        print(f"Size: {email_data['size']} bytes")
        print("-" * 50)
