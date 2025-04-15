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
        "approval": 2, "confirm": 2, "urgent": 3, "immediate": 3,
        "feedback": 1, "interview": 2, "offer letter": 2, "contract": 2,
        "ticket": 2, "support": 2, "bug": 2, "outage": 3, "failure": 2,
        "shipment": 1, "order": 1, "assigned": 1, "task": 2,
        "reset your password": 2, "account locked": 3, "login attempt": 2,
        "error": 2, "fix": 2, "update": 2, "upgrade": 2, "renew": 2,
        "appointment": 2, "schedule": 2, "meeting": 2, "calendar": 2,
        "verify": 2,
    }

    # Negative weighted keywords (promotions, spam, marketing)
    spam_keywords = {
        "unsubscribe": -3, "newsletter": -2, "noreply": -2, "auto-generated": -2,
        "promotion": -2, "discount": -2, "sale": -2, "exclusive": -2,
        "download": -2, "free": -2, "deal": -2, "offer": -2, "coaching": -2,
        "reflection worksheet": -3, "free resource": -3, "become a member": -3,
        "limited time": -2, "reward": -2, "bonus": -2, "click here": -2,
        "webinar": -2, "join now": -2, "register": -2, "watch now": -2
    }

    def keyword_score(text, keywords):
        score = 0
        if not text:
            return score
        for keyword, weight in keywords.items():
            if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
                score += weight
        return score

    # ✉️ Score sender trust
    if sender:
        sender_lower = sender.lower()
        if gmail_user and gmail_user.lower() in sender_lower:
            return 10
        if "no-reply" in sender_lower or "noreply" in sender_lower or "newsletter" in sender_lower:
            score -= 3
        if my_email and my_email.lower() in sender_lower:
            score -= 2
        if any(domain in sender_lower for domain in ["virtualvocations", "hubspot", "mailchimp", "convertkit", "clickfunnels"]):
            score -= 3

    # 🧠 Score subject & body based on weighted keywords
    score += keyword_score(subject, important_keywords)
    score += keyword_score(body, important_keywords)
    score += keyword_score(subject, spam_keywords)
    score += keyword_score(body, spam_keywords)

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

    return score > 0