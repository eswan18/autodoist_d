import os
import yaml
import todoist
import utils

api_token = os.environ['TODOIST_API_TOKEN']
CONFIG_DIR = 'config_files'

# Setup.
api = todoist.TodoistAPI(api_token)
api.sync()

# Load the config.
with open('config.yml') as f:
    conf = yaml.load(f)

# Fetch the current versions of projects, items, and labels.
labels = api.labels.all()
projects = api.projects.all()
items = api.items.all()

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

####################################################################
# Instantiate templates
####################################################################
for template in conf['template-instantiations']:
    project = utils.get_project_by_name(template['existing-project-name'],
                                        projects)
    template_filename = CONFIG_DIR + '/' + template['template-file']
    api.templates.import_into_project(project['id'], template_filename)
