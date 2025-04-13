import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

gmail_user = os.getenv("EMAIL_ADDRESS")
gmail_app_password = os.getenv("EMAIL_PASSWORD")
# gmail_user = os.getenv("GMAIL_USER")
# gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")

def send_email_via_smtp(sender_name, sender_email, recepient_email, deadline, task):
    if not gmail_user or not gmail_app_password:
        raise Exception("SMTP credentials not set in environment variables.")
    
    subject = "New Task from Sortify"
    body = f"""New Task Received via Sortify\n\nFrom: {sender_name} ({sender_email})\nTask: {task}\nDue: {deadline}\n\nThis task will appear in your Sortify dashboard automatically.\n"""
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = f"{sender_name} <{sender_email}>"
    msg['To'] = recepient_email
    revised_body = body.replace('\n', ' ').replace('\r', ' ')
    msg['X-Email-Body'] = Header(revised_body, 'utf-8').encode()
    msg.attach(MIMEText(body, 'plain'))
    email_text = msg.as_string()
    
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_app_password)
    server.sendmail(sender_email, recepient_email, email_text)
    server.quit() 