# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

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


def fetch(api):
    labels = api.labels.all()
    projects = api.projects.all()
    items = api.items.all()
    return labels, projects, items

def send_email(msg):
    msg = MIMEText(to, from_, subject, msg)

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = subject
    msg['From'] = from_
    msg['To'] = to

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], msg.as_string())
    s.quit()
