import os
import openai
from datetime import datetime, timedelta
import logging
from tasks.utils import is_important_email

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_tasks(email_body):
    logging.debug("Processing emails...")

    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that extracts one actionable task from an email and formats it as a standardized to-do item.\n\n"
                "Rules:\n"
                "- The task should start with an **actionable verb** (e.g., Reply, Confirm, Submit, Schedule).\n"
                "- Keep it **short and clear**, like a task you’d write in a to-do list.\n"
                "- If the email expects a response (e.g., 'Let me know', 'Please reply', 'Can you confirm?'), treat it as a task like 'Reply to...'.\n"
                "- Include any **deadlines or details** if explicitly mentioned.\n"
                "- Do not include irrelevant or redundant information.\n"
                "- If there’s **no actionable task**, return: 'No actionable tasks.'\n\n"
                "Format example: Reply to Jane’s request about the event schedule by April 15th."
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
    # logging.debug("Extracted Tasks:\n%s", tasks)
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
        # normalized_deadlines = extract_deadline_with_chatgpt(extracted_tasks)
        normalized_deadlines = "N/A"

        # Summarize tasks with deadlines
        # task_summary = summarize_tasks(extracted_tasks)

        print("\nFinal Summary:\n", extracted_tasks)
        print("\nDeadline:\n", normalized_deadlines)
    else:
        print("Email is not important; skipping processing.")
