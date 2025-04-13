from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from tasks.email_reader import fetch_emails
from tasks.ai_processor import extract_tasks, summarize_tasks, extract_deadline_with_chatgpt
from tasks.sortify_processor import extract_sortify_task
from tasks.email_sender import send_email_via_smtp
import os
import logging
import smtplib

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    logging.debug("Rendering index page.")
    return render_template("index.html")

@app.route("/fetch-emails", methods=["POST"])
def fetch_and_process_emails():
    try:
        data = request.json
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        last_updated = data.get("last_updated")
        logging.debug("Received fetch_emails request; access token provided: %s", bool(access_token))
        
        logging.info(last_updated)
        if not access_token:
            return jsonify({"error": "Access token is required."}), 401
        
        # Step 1: Fetch emails
        emails = fetch_emails(access_token, refresh_token, last_updated)
        logging.debug("Fetched %d emails from Gmail API", len(emails))

        # Step 2: Process each email
        actionable_tasks = []
        for email in emails:
            logging.debug("Processing email from: %s with subject: %s", email.get("from"), email.get("subject"))
            if email.get("subject").lower() == "new task from sortify":
                detailed_tasks, deadline = extract_sortify_task(email["body"])
                actionable_tasks.append({
                    "subject": email["subject"],
                    "from": email["from"],
                    "summary": detailed_tasks,
                    "deadline": deadline if deadline else "No deadline"
                })
            else:
                detailed_tasks = extract_tasks(email["body"])  # Extract detailed tasks
                if "No actionable tasks" not in detailed_tasks:  # Filter out non-actionable tasks
                    deadline = extract_deadline_with_chatgpt(detailed_tasks)  # Extract deadline
                    actionable_tasks.append({
                        "subject": email["subject"],
                        "from": email["from"],
                        "summary": detailed_tasks,
                        "deadline": deadline if deadline else "No deadline"
                    })

        # Step 4: Structure response
        response = {
            "tasks": actionable_tasks,  # Includes per-email summaries
        }

        logging.debug("Returning response with %d actionable tasks", len(actionable_tasks))
        # Return the response as JSON
        return jsonify(response)
    except Exception as e:
        logging.error("Error in fetch_and_process_emails: %s", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/fetch-old-emails", methods=["POST"])
def fetch_old_emails():
    try:
        data = request.json
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        first_updated = data.get("first_updated")
        logging.debug("Received fetch_old_emails request; access token provided: %s", bool(access_token))
        
        logging.info(first_updated)
        if not access_token:
            return jsonify({"error": "Access token is required."}), 401
        
        # Fetch emails using first_updated instead of last_updated
        emails = fetch_emails(access_token, refresh_token, first_updated)
        logging.debug("Fetched %d emails from Gmail API", len(emails))

        # Process each email
        actionable_tasks = []
        for email in emails:
            logging.debug("Processing email from: %s with subject: %s", email.get("from"), email.get("subject"))
            if email.get("subject").lower() == "new task from sortify":
                detailed_tasks, deadline = extract_sortify_task(email["body"])
                actionable_tasks.append({
                    "subject": email["subject"],
                    "from": email["from"],
                    "summary": detailed_tasks,
                    "deadline": deadline if deadline else "No deadline"
                })
            else:
                detailed_tasks = extract_tasks(email["body"])  # Extract detailed tasks
                if "No actionable tasks" not in detailed_tasks:  # Filter out non-actionable tasks
                    deadline = extract_deadline_with_chatgpt(detailed_tasks)  # Extract deadline
                    actionable_tasks.append({
                        "subject": email["subject"],
                        "from": email["from"],
                        "summary": detailed_tasks,
                        "deadline": deadline if deadline else "No deadline"
                    })
        
        response = {"tasks": actionable_tasks}
        logging.debug("Returning response with %d actionable tasks", len(actionable_tasks))
        return jsonify(response)
    except Exception as e:
        logging.error("Error in fetch_old_emails: %s", str(e))
        return jsonify({"error": str(e)}), 500

# New endpoint to send an email via Gmail SMTP
@app.route("/send-email", methods=["POST"])
def send_email():
    try:
        data = request.json
        sender_name = data.get("sender_name")
        sender_email = data.get("sender_email")
        recepient_email = data.get("recepient_email")
        deadline = data.get("deadline")
        task = data.get("task")
        
        if not all([sender_name, sender_email, recepient_email, deadline, task]):
            return jsonify({"error": "All fields are required."}), 400
        
        send_email_via_smtp(sender_name, sender_email, recepient_email, deadline, task)
        
        return jsonify({"message": "Email sent successfully."})
    except Exception as e:
        logging.error("Error in send-email endpoint: %s", str(e))
        return jsonify({"error": "Failed to send email."}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5174))
    logging.info("Starting server on host 0.0.0.0 and port %d", port)
    app.run(host="0.0.0.0", port=port)
