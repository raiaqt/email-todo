import logging
import re

def extract_sortify_task(email_body: str):
    """Extracts the task and due date from a Sortify email body.

    Expected email body format:

    Hi there,

    {sender_name} ({sender_email}) just shared a task with you via Sortify:

    Task: {task}  
    Due: {deadline}

    This task will be available on your Sortify dashboard.

    Returns:
        A list [detailed_task, deadline] where detailed_task is formatted as
        "Review the Q2 report (sent by Raia)" and deadline is the due date string.
    """
    sender = ""
    task = ""
    deadline = ""

    for line in email_body.splitlines():
        logging.debug(f"Line: {line}")
        line = line.strip()

        # Match the sender line
        match_sender = re.match(r"^(.*) \((.*)\) just shared a task", line)
        if match_sender:
            sender = match_sender.group(1).strip()

        elif line.startswith("Task:"):
            task = line[len("Task:"):].strip()

        elif line.startswith("Due:"):
            deadline = line[len("Due:"):].strip()

    logging.debug(f"Sender: {sender}, Task: {task}, Deadline: {deadline}")
    detailed_task = f"{task} (sent by {sender})" if task and sender else task
    return [detailed_task, deadline]
