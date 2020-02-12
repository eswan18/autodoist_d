from typing import Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Console Handler
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

def update_templates(user, conf):
    '''Automatically label tasks in projects.

    Parameters
    ----------
    user : pytodoist.todoist.user
        A Todoist user object, used for interacting with Todoist.
    conf : dict[str: Any]
        An application configuration. Specifically needs to have a
        project-label key.
    '''
    logger.info('Started update job.')
    for record in conf['project-label']:
        project_name, label_name = record['project'], record['label']
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
                log_str = log_str.format(task.content,
                                         project_name,
                                         label_name)
                logger.debug(log_str)
    logger.info('Completed update job.')

def missing_due_date_alert(user, conf):
    print('Starting missing due date alert')
    # We need to keep track of the tasks we've already seen -- can be done by
    # setting an attribute of the function.
    try:
        seen_ids = missing_due_date_alert.seen_ids
    # The first time the function runs, this attribute won't exist yet and
    # needs to be initialized.
    except AttributeError:
        seen_ids = []
    # Get uncompleted tasks without a due date.
    undue_tasks = [task for task in user.get_tasks()
                   if not task.checked and task.due is None]
    # Determine which haven't been seen before, and record them.
    unseen_tasks = [task for task in undue_tasks
                    if task.id not in seen_ids]
    seen_ids.extend([task.id for task in unseen_tasks])
    missing_due_date_alert.seen_ids = seen_ids
    #missing_due_date_alert.seen_ids = seen_ids
    for task in unseen_tasks:
        s = (f'You added a task "{task.content}" to project '
             f'{task.project.name} without a due date. Was this intentional?')
        print(s)


# Create a record class.
# I would have liked to use a named tuple here but the immutability turned out
# to be annoying.
@dataclass
class FuncJob:
    '''Class for tracking job definitions.'''
    name: str
    func: Callable
    cron: str

# Add all jobs into a single list.
jobs = [FuncJob('Update Templates', update_templates, '*/5 * * * *'),
        FuncJob('Missing Due Date Alert', missing_due_date_alert, '* * * * *')]
# Note that this could be more elegantly implemented as a decorator for each
# task function.

