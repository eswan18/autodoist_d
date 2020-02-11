# Builtins
import os
import time
import logging
import argparse
import pathlib
# Installed
import yaml
from pytodoist import todoist
# Project libraries
import utils
from job_queue import JobQueue

API_TOKEN = os.environ['TODOIST_API_TOKEN']
EMAIL_ADDR = os.environ['EMAIL_ADDR']
EMAIL_PW = os.environ['EMAIL_PW']
CONFIG_DIR = pathlib.Path('./config')
TEMPLATE_DIR = pathlib.Path('./config/templates')

# Email self to alert that Autodoist has restarted.
utils.send_email(from_=EMAIL_ADDR, to=EMAIL_ADDR,
                 subject='Autodoist Restarted',
                 body='Autodoist Restarted',
                 user=EMAIL_ADDR, password=EMAIL_PW)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Console Handler
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
####################################################################
# Command line arguments
####################################################################
parser = argparse.ArgumentParser(description='Automate Todoist workflows.')
parser.add_argument('--loglevel', dest='loglevel', nargs=1,
                    help='set a log level')
args = parser.parse_args()

# If the user specified a log level, use it.
if args.loglevel is not None:
    loglevel, *rest = args.loglevel
    ch.setLevel(loglevel.upper())
# Register the console handler with the logger.
logger.addHandler(ch)

# Setup.
user = todoist.login_with_api_token(API_TOKEN)
logger.info('Synced with Todoist.')
q = JobQueue()

# Load the config.
with open(CONFIG_DIR / 'config.yml') as f:
    conf = yaml.load(f, Loader=yaml.SafeLoader)
logger.debug('Loaded config file.')


def update():
    logger.info('Started update job.')
    ####################################################################
    # Auto-label items in projects
    ####################################################################
    for pl_map in conf['project-label']:
        project_name, label_name = pl_map['project'], pl_map['label']
        # Tasks in the project in question.
        tasks = user.get_project(project_name).get_tasks()
        label_id = user.get_label(label_name).id
        # Make sure every item has the required label. If not, add it.
        for task in tasks:
            if label_id not in task.labels:
                task.labels = task.labels + [label_id]
                # Sync to Todoist
                task.update()
                log_str = 'Labeled task "{}" in project "{}" as "{}".'
                log_str = log_str.format(task.content,
                                         project_name,
                                         label_name)
                logger.debug(log_str)
    logger.info('Completed update job.')


# Add the update function to the job queue. It should run every 5 minutes.
q.add_job(job_name='Update Templates', job_func=update,
          job_cron='*/5 * * * *')

####################################################################
# Instantiate templates
####################################################################
labels = user.get_labels()
projects = user.get_projects()
for template in conf['template-instantiations']:
    project = user.get_project(template['existing-project-name'])
    template_filename = TEMPLATE_DIR / template['template-file']
    def import_template():
        log_str = 'Started importing template from file {}'
        logger.info(log_str.format(template_filename))
        api.templates.import_into_project(project['id'], template_filename)
    job_name = 'Import ' + template['existing-project-name']
    job_func = import_template
    job_cron = template['cron']
    q.add_job(job_name=job_name, job_func=job_func, job_cron=job_cron)

while True:
    # Run at most every minute.
    logger.debug('Running pending job queue jobs.')
    q.run_pending()
    time.sleep(60)
