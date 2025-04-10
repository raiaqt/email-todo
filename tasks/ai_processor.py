import os
import openai
from datetime import datetime, timedelta
import logging

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_tasks(email_body):
    logging.debug("Processing emails...")

    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that extracts actionable tasks from emails and formats them as a standardized to-do list. "
                "Each task should be a concise numbered list starting with an actionable verb. "
                "Each task should be a short simple sentence. "
                "Include any relevant deadlines or details if mentioned. "
                "Do not include irrelevant or redundant details. "
                "If no actionable tasks are found, respond with 'No actionable tasks'. "
                "Format example:\n"
                "1. Submit the project report by January 20th.\n"
                "2. Schedule a meeting with the marketing team for next week.\n"
                "3. Follow up with the client regarding the contract terms.\n"
            )
        },
        {
            "role": "user",
            "content": f"Here is the email content:\n\n{email_body}"
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.1,
        max_tokens=1500,
    )

    tasks = response['choices'][0]['message']['content'].strip()
    logging.debug("Extracted Tasks:\n%s", tasks)
    return tasks


def extract_deadline_with_chatgpt(tasks):
    """
    Uses ChatGPT to extract and normalize deadlines from the task list.
    Converts phrases like 'tomorrow' or 'next week' into actual dates.
    """
    logging.debug("Extracting deadlines...")

    messages = [
         {
            "role": "system",
            "content": (
                "You are an assistant that extracts a single deadline from a to-do list. "
                "If there are multiple deadlines, select the most relevant one (e.g., the earliest deadline). "
                "Convert all vague time expressions like 'tomorrow,' 'next week,' or 'end of the week' into specific dates. "
                "Return only the date in the format 'YYYY-MM-DD' (e.g., 2025-01-20). "
                "Do not include any other text or explanations."
            )
        },
        {
            "role": "user",
            "content": f"Here is the to-do list:\n\n{tasks}"
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.1,
        max_tokens=150,
    )

    deadlines = response['choices'][0]['message']['content'].strip()
    logging.debug("Extracted Deadlines:\n%s", deadlines)
    return deadlines


def summarize_tasks(tasks,):
    """
    Summarizes tasks into a single sentence and includes the deadline if available.
    """
    logging.debug("Summarizing tasks...")

    messages = [
          {
            "role": "system",
            "content": (
                "You are an assistant that generates a single concise and action-oriented sentence summarizing a to-do list. "
                "Analyze each task, identify the central theme or purpose of the list, and craft a summary that reflects the shared focus of the tasks. "
                "The summary should start with a verb (e.g., Prepare, Coordinate, Analyze, Review) and include specific keywords related to the theme. "
                "Do not list individual tasks; instead, generalize their purpose into a cohesive statement that captures their intent."
            )
        },
        {
            "role": "user",
            "content": f"Here is the to-do list:\n\n{tasks}"
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.1,
        max_tokens=100,  # Ensure brevity
    )

    summary = response['choices'][0]['message']['content'].strip()
    logging.debug("Task Summary:\n%s", summary)
    return summary


# NEW FUNCTION: Filter emails based on importance
def is_important_email(email_body, sender=None, my_email=None):
    """Determines if an email is important by checking for spam or subscription related keywords.
    Returns True if no spam keywords are found and the sender is not automated.
    """
    spam_keywords = ["unsubscribe", "newsletter", "no-reply", "auto-generated", "promotion", "sale"]
    if any(keyword.lower() in email_body.lower() for keyword in spam_keywords):
        return False
    if sender and ("no-reply" in sender.lower() or "noreply" in sender.lower()):
        return False
    if my_email and my_email.lower() in sender.lower():
        return False
    return True


# Modify the __main__ block to use email importance filtering
if __name__ == "__main__":
    email_content = """
    Hi John,

    Please complete the following tasks:
    1. Submit the Q4 report by January 20, 2025.
    2. Schedule a follow-up meeting with the marketing team next week.
    3. Update the client contract with the new terms by end of the week.
    4. Review the draft proposal and send your feedback by tomorrow.

    Let me know if you have any questions.

    Best,
    Jane
    """
    
    # Added sender info for filtering (assuming email header or sender info is available)
    sender = "Jane <jane@example.com>"

    if is_important_email(email_content, sender, my_email="john@example.com"):
        # Extract tasks
        extracted_tasks = extract_tasks(email_content)

        # Extract deadlines
        normalized_deadlines = extract_deadline_with_chatgpt(extracted_tasks)

        # Summarize tasks with deadlines
        task_summary = summarize_tasks(extracted_tasks)

        print("\nFinal Summary:\n", task_summary)
        print("\nDeadline:\n", normalized_deadlines)
    else:
        print("Email is not important; skipping processing.")
