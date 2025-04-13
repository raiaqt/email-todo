import logging

def extract_sortify_task(email_body: str):
    """Extracts the task and due date from a Sortify email body.

    Expected email body format:

    New Task Received via Sortify

    From: Raia (raia@example.com)
    Task: Review the Q2 report
    Due: Friday, April 15

    This task will appear in your Sortify dashboard automatically.

    Returns:
        A list [detailed_task, deadline] where detailed_task is formatted as "Review the Q2 report (sent by Raia)" and deadline is the due date string.
    """
    sender = ""
    task = ""
    deadline = ""

    for line in email_body.splitlines():
        logging.debug(f"Line: {line}")
        line = line.strip()
        if line.startswith("From:"):
            content = line[len("From:"):].strip()
            if "(" in content:
                sender = content.split("(")[0].strip()
            else:
                sender = content
        elif line.startswith("Task:"):
            task = line[len("Task:"):].strip()
        elif line.startswith("Due:"):
            deadline = line[len("Due:"):].strip()

    logging.debug(f"Sender: {sender}, Task: {task}, Deadline: {deadline}")
    detailed_task = f"{task} (sent by {sender})" if task and sender else task
    return [detailed_task, deadline]
