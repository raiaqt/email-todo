import re
import os

gmail_user = os.getenv("EMAIL_ADDRESS")

def score_email_importance(subject, body, sender=None, my_email=None):
    """
    Scores an email based on importance signals.
    Returns a numeric score — process only if score > 0.
    """

    score = 1

    # Positive weighted keywords (actionable or important)
    important_keywords = {
        "invoice": 2, "payment": 2, "billing": 2, "reminder": 2,
        "domain": 2, "schedule": 2, "meeting": 2, "calendar": 2,
        "approval": 2, "confirm": 2, "urgent": 4, "immediate": 3,
        "feedback": 1, "interview": 2, "offer letter": 2, "contract": 2,
        "ticket": 2, "support": 2, "bug": 2, "outage": 3, "failure": 2,
        "shipment": 1, "order": 1, "assigned": 1, "task": 2,
        "reset your password": 2, "account locked": 3, "login attempt": 2,
        "error": 2, "fix": 2, "update": 2, "upgrade": 2, "renew": 2,
        "appointment": 2, "verify": 2, "invited": 3, "shared with you": 3,
        "accept": 2, "collaborate": 2, "error": 2, "fix": 2, "update": 2,
        "failed": 2, "notice": 4, "refund": 2, "final": 4, "mentioned": 4,
        "mentioned you in a comment": 6
    }

    # Negative weighted keywords (promotions, spam, marketing)
    spam_keywords = {
        "unsubscribe": -10, "subscription": -6, "subscribed": -6,
        "newsletter": -6, "noreply": -4, "auto-generated": -4,
        "promotion": -5, "discount": -6, "sale": -6, "exclusive": -6,
        "download": -5, "free": -6, "deal": -6, "offer": -6, "coaching": -5,
        "become a member": -6, "limited time": -5, "reward": -5,
        "bonus": -5, "click here": -5, "webinar": -4, "join now": -4,
        "register": -4, "watch now": -4, "complete order": -6,
        "order now": -6, "order completed": -6, "shop": -6,
        "checkout": -6, "cart": -6, "buy now": -6, "clearance": -5,
        "get access": -5, "premium subscription": -5, "code to log in": -5
    }

    def keyword_score(text, keywords):
        score = 0
        if not text:
            return score
        for keyword, weight in keywords.items():
            if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                score += weight
        return score

    # 📉 Score common numeric discount formats (e.g., 1200 OFF)
    def pattern_score(text):
        score = 0
        if not text:
            return score
        patterns = [
            r"\b\d{2,4}\s*off\b",  # e.g., 1200 OFF, 50 off
            r"\bup to\s*\d{1,4}%\s*off\b",  # e.g., up to 70% off
            r"\bsave\s*\d{1,4}\b",  # e.g., save 100
            r"\b\d{2,4}%\s*discount\b",
        ]
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score -= 6
        return score

    # ✉️ Score sender trust
    if sender:
        sender_lower = sender.lower()
        if gmail_user and gmail_user.lower() in sender_lower:
            return 10
        if "no-reply" in sender_lower or "noreply" in sender_lower or "newsletter" in sender_lower:
            score -= 2
        if my_email and my_email.lower() in sender_lower:
            score -= 2
        if any(domain in sender_lower for domain in [
            "workingnomads.com", "sheinemail.com", "maroonbluebook.com",
            "hubspot", "mailchimp", "convertkit", "clickfunnels"
        ]):
            score -= 5

    # 🧠 Score subject & body based on weighted keywords
    score += keyword_score(subject, important_keywords)
    score += keyword_score(body, important_keywords)
    score += keyword_score(subject, spam_keywords)
    score += keyword_score(body, spam_keywords)
    score += pattern_score(subject)
    score += pattern_score(body)

    return score

def is_important_email(email_subject, email_body, sender=None, my_email=None):
    """
    Determines if an email should be processed based on importance score.
    Uses a weighted scoring system to balance important and spam indicators.
    """

    score = score_email_importance(
        subject=email_subject or "",
        body=email_body or "",
        sender=sender,
        my_email=my_email or gmail_user
    )

    # Debug print (optional)
    # print(f"[DEBUG] Email scored {score} — Subject: {email_subject[:60]}")

    return score > 0
