from typing import Callable
from dataclasses import dataclass
import logging

from utils import send_email

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Console Handler
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def update_templates(user, conf):
    """Automatically label tasks in projects.

    Parameters
    ----------
    user : pytodoist.todoist.user
        A Todoist user object, used for interacting with Todoist.
    conf : dict[str: Any]
        An application configuration. Specifically needs to have a
        project-label key.
    """
    logger.info("Started update job.")
    for record in conf["project-label"]:
        project_name, label_name = record["project"], record["label"]
        # Tasks in the project in question.
        tasks = user.get_project(project_name).get_tasks()
        label_id = user.get_label(label_name).id
        # Make sure every item has the required label. If not, add it.
        for task in tasks:
            if label_id not in task.labels:
                # DO NOT CHANGE TO task.labels.append(...)
                # There is a pytodoist bug that means that doesn't work.
                task.labels = task.labels + [label_id]
                # Sync to Todoist
                task.update()
                log_str = 'Labeled task "{}" in project "{}" as "{}".'
                log_str = log_str.format(task.content, project_name, label_name)
                logger.debug(log_str)
    logger.info("Completed update job.")


def missing_due_date_alert(user, conf):
    logger.info("Started missing due date alert job.")
    # We need to keep track of the tasks we've already seen -- can be done by
    # setting an attribute of the function.
    try:
        seen_ids = missing_due_date_alert.seen_ids
    # The first time the function runs, this attribute won't exist yet and
    # needs to be initialized.
    except AttributeError:
        seen_ids = []
    # Get uncompleted tasks without a due date.
    undue_tasks = [
        task for task in user.get_tasks() if not task.checked and task.due is None
    ]
    # Determine which haven't been seen before, and record them.
    unseen_tasks = [task for task in undue_tasks if task.id not in seen_ids]
    seen_ids.extend([task.id for task in unseen_tasks])
    missing_due_date_alert.seen_ids = seen_ids
    if unseen_tasks:
        msg = "You added {n} tasks without due dates. Was this intentional?\n"
        msg = msg.format(n=len(unseen_tasks))
        msg += "New tasks without dates:\n"
        for task in unseen_tasks:
            content = task.content.encode(encoding="ascii", errors="replace").decode()
            project = task.project.name.encode(
                encoding="ascii", errors="replace"
            ).decode()
            msg += f'  - "{content}" in project "{project}"\n'
        send_email(
            from_=conf["email_addr"],
            to=conf["email_addr"],
            user=conf["email_addr"],
            password=conf["email_pw"],
            body=msg,
            subject="Autodoist: Tasks Without Due Dates",
        )
    # Eventually these log statements should be handled by the decorator that
    # adorns these job functions.
    logger.info("Finished missing due date alert job.")


# Create a record class.
# I would have liked to use a named tuple here but the immutability turned out
# to be annoying.
@dataclass
class FuncJob:
    """Class for tracking job definitions."""

    name: str
    func: Callable
    cron: str


# Add all jobs into a single list.
jobs = [
    FuncJob("Update Templates", update_templates, "*/5 * * * *"),
    FuncJob("Missing Due Date Alert", missing_due_date_alert, "* * * * *"),
]
# Note that this could be more elegantly implemented as a decorator for each
# task function.
