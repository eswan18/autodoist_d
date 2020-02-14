# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

def send_email(from_, to, subject, body, user, password):
    email_text = f'''Subject: {subject}\n\n{body}
    '''
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(user, password)
    server.sendmail(from_, to, email_text)
    server.close()
