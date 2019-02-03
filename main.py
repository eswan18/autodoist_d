import os

api_token = os.environ['TODOIST_API_TOKEN']

api = todoist.TodoistAPI(api_token)
api.sync()


