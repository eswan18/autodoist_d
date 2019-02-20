from datetime import datetime
from croniter import croniter

class JobQueue():

    def __init__(self, jobdict=None):
        if jobdict is None:
            jobdict = {}
        self.jobdict = jobdict

    def add_job(self, job_name, job_func, job_cron):
        job_iter = croniter(job_cron)
        job = {job_name: {'func': job_func,
                          'cron': job_cron,
                          'iter': job_iter,
                          'next': job_iter.get_next()
                          }
              }
        self.jobdict.update(job)
