import os
import openai
from datetime import datetime
import logging
from tasks.utils import is_important_email

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
today_str = datetime.today().strftime('%Y-%m-%d')


def extract_tasks(email_body):
    logging.debug("Processing emails...")

    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that extracts **one actionable task** from an email and formats it as a standardized to-do item.\n\n"
                "Guidelines:\n"
                "- The task must begin with an **actionable verb** (e.g., Reply, Confirm, Submit, Schedule).\n"
                "- Keep it **short and clear**, like something you would add to a task list.\n"
                "- If the email contains a **question** or any **request for a reply** — even subtle phrases like:\n"
                "  'Let me know', 'Can you confirm?', 'Do you agree?', 'Is that okay with you?', 'What do you think?' —\n"
                "  then treat it as: 'Reply to sender...'\n"
                "- These phrases **always** imply an action, even if the word 'reply' is not used.\n"
                "- Include deadlines or dates if they are mentioned explicitly (e.g., 'by Friday, April 14').\n"
                "- If there is **no actionable task**, return this exact string: 'No actionable tasks.'\n\n"
                "Format example:\n"
                "Submit the updated sales forecast by May 1st.\n"
                "Reply to Jane's question about the budget timeline by April 15th."
            )
        },
        {
            "role": "user",
            "content": f"Here is the email content:\n\n{email_body}"
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1,
            max_tokens=1500,
        )
        tasks = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logging.error("Error calling openai API in extract_tasks: %s", e)
        tasks = "No actionable tasks."

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
                f"You are an assistant that extracts a single deadline from a to-do list.\n"
                f"Today's date is {today_str}.\n"
                "If there are multiple deadlines, select the most relevant one (e.g., the earliest).\n"
                "Convert all vague expressions like 'tomorrow', 'next week', or 'Friday' into an actual date.\n"
                "Return only the date in this format: 'YYYY-MM-DD' (e.g., 2025-01-20).\n"
                "Do not include any explanation or extra text.\n"
                "Never return a date earlier than today. If a deadline has passed, ignore it and return no deadline."
            )
        },
        {
            "role": "user",
            "content": f"Here is the to-do list:\n\n{tasks}"
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1,
            max_tokens=150,
        )
        deadlines = response['choices'][0]['message']['content'].strip()
        logging.debug("Extracted Deadlines:\n%s", deadlines)
    except Exception as e:
        logging.error("Error calling openai API in extract_deadline_with_chatgpt: %s", e)
        deadlines = ""

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

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1,
            max_tokens=100,  # Ensure brevity
        )
        summary = response['choices'][0]['message']['content'].strip()
        logging.debug("Task Summary:\n%s", summary)
    except Exception as e:
        logging.error("Error calling openai API in summarize_tasks: %s", e)
        summary = "No summary available."

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
