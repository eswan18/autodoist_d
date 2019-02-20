# Builtins
import os
import time
import logging
import argparse
# Installed
import yaml
import todoist
import croniter
# Project libraries
import utils

API_TOKEN = os.environ['TODOIST_API_TOKEN']
CONFIG_DIR = 'config_files'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Console Handler
ch = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
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
logger.info('Synced with Todoist.')

# Setup.
api = todoist.TodoistAPI(API_TOKEN)
api.sync()
logger.info('Synced with Todoist.')

# Load the config.
with open('config.yml') as f:
    conf = yaml.load(f)
logger.debug('Loaded config file.')


def update():
    logger.info('Started update job.')
    # Fetch the current versions of projects, items, and labels.
    labels = api.labels.all()
    projects = api.projects.all()
    items = api.items.all()
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
    api.commit()
    logger.info('Committed to Todoist. Completed update job.')



####################################################################
# Instantiate templates
####################################################################
#for template in conf['template-instantiations']:
#    project = utils.get_project_by_name(template['existing-project-name'],
#                                        projects)
#    template_filename = CONFIG_DIR + '/' + template['template-file']
#    api.templates.import_into_project(project['id'], template_filename)

# Use the schedule module to handle the looping.
while True:
    # Run at most every 5 minutes.
    time.sleep(5 * 60)
