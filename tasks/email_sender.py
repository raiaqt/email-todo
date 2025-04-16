import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

gmail_user = os.getenv("EMAIL_ADDRESS")
gmail_app_password = os.getenv("EMAIL_PASSWORD")

def send_email_via_smtp(sender_name, recipient_email, deadline, task):
    if not gmail_user or not gmail_app_password:
        raise Exception("SMTP credentials not set in environment variables.")

    subject = f"You’ve got a task from {sender_name}"

    if deadline==None:
        deadline = "No deadline"

    # Plain text version
    text_body = f"""
Hi there,

{sender_name} just shared a task with you via Sortify:

Task: {task}
Due: {deadline}

This task will be available on your Sortify dashboard.

Thanks for using Sortify!
"""

    # HTML version
    html_body = f"""
<html>
  <body>
    <p>Hi there,</p>
    <p><strong>{sender_name}</strong> just shared a task with you via <strong>Sortify</strong>:</p>
    <ul>
      <li><strong>Task:</strong> {task}</li>
      <li><strong>Due:</strong> {deadline}</li>
    </ul>
    <p>This task will appear in your Sortify dashboard.</p>
    <p style="color:#888;">Thanks for using Sortify!</p>
  </body>
</html>
"""

    # Compose the message
    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = f"Raia Quitoriano <{gmail_user}>"
    msg['To'] = recipient_email
    msg['Date'] = formatdate(localtime=True)
    msg['MIME-Version'] = '1.0'

    msg.attach(MIMEText(text_body.strip(), 'plain'))
    msg.attach(MIMEText(html_body.strip(), 'html'))

    # Send the email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_app_password)
        server.sendmail(gmail_user, recipient_email, msg.as_string())
