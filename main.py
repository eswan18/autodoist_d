import os
import yaml
import todoist

api_token = os.environ['TODOIST_API_TOKEN']

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
# First convert the label-project list into a mapping.
label_project = {entry['project']: entry['label']
                 for entry in conf['label-project']}

# Iterate through the projects, skipping the ones that aren't in the mapping.
for project in projects:
    if project['name'] in label_project:
        project_items = [item for item in items
                         if item['project_id'] == project['id']]
        print(project)
        print([item['content'] for item in project_items])
        break
