def get_project_by_name(p_name, projects):
    '''Find and return a project with name `p_name` from within `projects`.'''
    project = [project for project in projects
               if project['name'] == p_name][0]
    return project

def get_label_by_name(l_name, labels):
    '''Find and return a label with name `l_name` from within `labels`.'''
    label = [label for label in labels
               if label['name'] == l_name][0]
    return label

def get_items_by_project_id(p_id, items):
    return [item for item in items
            if item['project_id'] == p_id]
