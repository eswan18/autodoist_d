from typing import Callable
from dataclasses import dataclass

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
    #logger.info('Started update job.')
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
                #logger.debug(log_str)
    #logger.info('Completed update job.')

# Create a record class.
# I would have liked to use a named tuple here but the immutability of its
# attributes turned out to be annoying.
@dataclass
class FuncJob:
    '''Class for tracking job definitions.'''
    name: str
    func: Callable
    cron: str

# Add all jobs into a single list.
jobs = [FuncJob('Update Templates', update_templates, '*/5 * * * *')]
