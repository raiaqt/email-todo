from flask import Flask, render_template, request, jsonify
from tasks.email_reader import fetch_emails
from tasks.ai_processor import extract_tasks, summarize_tasks, extract_deadline_with_chatgpt
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/fetch-emails", methods=["POST"])
def fetch_and_process_emails():
    try:
        # Step 1: Fetch emails
        emails = fetch_emails()

        # Step 2: Process each email
        actionable_tasks = []
        for email in emails:
            detailed_tasks = extract_tasks(email["body"])  # Extract detailed tasks
            if "No actionable tasks" not in detailed_tasks:  # Filter out non-actionable tasks
                summary = summarize_tasks(detailed_tasks)  # Summarize the email's tasks
                deadline = extract_deadline_with_chatgpt(detailed_tasks)  # Extract deadline
                actionable_tasks.append({
                    "subject": email["subject"],
                    "from": email["from"],
                    "detailed_tasks": detailed_tasks,
                    "summary": summary,
                    "deadline": deadline if deadline else "No deadline"
                })

        # Step 4: Structure response
        response = {
            "tasks": actionable_tasks,  # Includes per-email summaries
        }

        # Return the response as JSON
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5173))  # Use the PORT environment variable or default to 5173
    app.run(host="0.0.0.0", port=port)
