# Builtins
import os
import time
import logging
import argparse
import pathlib
# Installed
import yaml
import todoist
# Project libraries
import utils
from job_queue import JobQueue

API_TOKEN = os.environ['TODOIST_API_TOKEN']
CONFIG_DIR = pathlib.Path('./config')
TEMPLATE_DIR = pathlib.Path('./config/templates')

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
api = todoist.TodoistAPI(API_TOKEN)
api.sync()
logger.info('Synced with Todoist.')
q = JobQueue()

# Load the config.
with open(CONFIG_DIR / 'config.yml') as f:
    conf = yaml.load(f)
logger.debug('Loaded config file.')


def update():
    logger.info('Started update job.')
    api.sync()
    logger.info('Synced with Todoist.')
    # Fetch the current versions of projects, items, and labels.
    labels, projects, items = utils.fetch(api)
    logger.info('Fetched labels, projects, and items from Todoist.')
    ####################################################################
    # Auto-label items in projects
    ####################################################################
    for pl_map in conf['project-label']:
        # Find the matching project and labels and get their IDs.
        project = utils.get_project_by_name(pl_map['project'], projects)
        label = utils.get_label_by_name(pl_map['label'], labels)
        project_items = utils.get_items_by_project_id(project['id'], items)
        # Make sure every item has the required label. If not, add it.
        for item in project_items:
            if label['id'] not in item['labels']:
                item.update(labels=item['labels'] + [label['id']])
                log_str = 'Labeled item "{}" in project "{}" as "{}".'
                log_str = log_str.format(item['content'],
                                         project['name'],
                                         label['name'])
                logger.debug(log_str)
    api.commit()
    logger.info('Committed to Todoist. Completed update job.')


# Add the update function to the job queue. It should run every 5 minutes.
q.add_job(job_name='Update Templates', job_func=update,
          job_cron='*/5 * * * *')

####################################################################
# Instantiate templates
####################################################################
labels, projects, items = utils.fetch(api)
for template in conf['template-instantiations']:
    project = utils.get_project_by_name(template['existing-project-name'],
                                        projects)
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
