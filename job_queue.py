from datetime import datetime
from croniter import croniter
import pytz

class JobQueue():

    def __init__(self, jobdict=None):
        if jobdict is None:
            jobdict = {}
        self.jobdict = jobdict

    def add_job(self, job_name, job_func, job_cron):
        if job_name in self.jobdict:
            raise ValueError(f'Job name {job_name} already exists.')
        # Convert the current time to UTC so the math works.
        current_time = datetime.now().astimezone(pytz.utc)
        # Create a croniter object for the job
        job_iter = croniter(job_cron, current_time)
        # Build a dictionary of one key, which we can use to update the master
        # jobdict.
        job = {job_name: {'func': job_func,
                          'cron': job_cron,
                          'iter': job_iter,
                          'next': job_iter.get_next(datetime)
                          }
              }
        self.jobdict.update(job)

    def run_pending(self):
        for name, job in self.jobdict.items():
            # Execute any jobs that are due.
            if job['next'] < datetime.now().astimezone(pytz.utc):
                print(f'Executing at {datetime.now()}!')
                # First, update the next value.
                job['next'] = job['iter'].get_next(datetime)
                # Then run the function.
                job['func']()

    def __str__(self):
        s = '<JobQueue with {} jobs>'
        s = s.format(len(self.jobdict))
        return s

    def __repr__(self):
        return f'JobQueue({repr(self.jobdict)})'
