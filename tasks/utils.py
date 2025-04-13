import re
import os

gmail_user = os.getenv("EMAIL_ADDRESS")

def is_important_email(email_subject, email_body, sender=None, my_email=None):
    """Determines if an email is important by checking for spam or subscription-related keywords."""
    if sender and gmail_user in sender:
        return True

    spam_keywords = [
        "unsubscribe", "newsletter", "no-reply", "auto-generated",
        "promotion", "promotions", "sale", "social",
        "updates", "offer", "discount", "deal"
    ]

    # Match spam keywords as whole words (not substrings)
    pattern = r'\b(' + '|'.join(spam_keywords) + r')\b'

    if re.search(pattern, email_subject, re.IGNORECASE):
        return False
    if re.search(pattern, email_body, re.IGNORECASE):
        return False
    if sender and ("no-reply" in sender.lower() or "noreply" in sender.lower()):
        return False
    if my_email and my_email.lower() in sender.lower():
        return False

    return True
