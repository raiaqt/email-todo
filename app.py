from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from tasks.email_reader import fetch_emails
from tasks.ai_processor import extract_tasks, summarize_tasks, extract_deadline_with_chatgpt
import os
import logging

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
        last_updated = data.get("last_updated")
        logging.debug("Received fetch_emails request; access token provided: %s", bool(access_token))
        
        logging.info(last_updated)
        if not access_token:
            return jsonify({"error": "Access token is required."}), 400
        
        # Step 1: Fetch emails
        emails = fetch_emails(access_token, last_updated)
        logging.debug("Fetched %d emails from Gmail API", len(emails))

        # Step 2: Process each email
        actionable_tasks = []
        for email in emails:
            logging.debug("Processing email from: %s with subject: %s", email.get("from"), email.get("subject"))
            detailed_tasks = extract_tasks(email["body"])  # Extract detailed tasks
            if "No actionable tasks" not in detailed_tasks:  # Filter out non-actionable tasks
                # summary = summarize_tasks(detailed_tasks)  # Summarize the email's tasks
                deadline = extract_deadline_with_chatgpt(detailed_tasks)  # Extract deadline
                actionable_tasks.append({
                    "subject": email["subject"],
                    "from": email["from"],
                    # "detailed_tasks": detailed_tasks,
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


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5174))
    logging.info("Starting server on host 0.0.0.0 and port %d", port)
    app.run(host="0.0.0.0", port=port)
