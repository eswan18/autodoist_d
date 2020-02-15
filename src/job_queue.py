from datetime import datetime
from croniter import croniter
import pytz

import logging


class JobQueue:
    """
    A queue of jobs to be run at regular intervals.
    """

    def __init__(self, jobdict=None, logger=None):
        if jobdict is None:
            jobdict = {}
        self.jobdict = jobdict
        if logger is None:
            logger = logging.getLogger(__name__)
        self.logger = logger

    def add_job(
        self, job_name=None, job_func=None, job_cron=None, job=None, day_or=True
    ):
        """
        Add a new job to the queue.

        Parameters
        ----------
        job_name : str
            A name for the job.
        job_func : Callable
            A callable to be executed when the job is run.
        job_cron : str
            A string in cron-format indicating the cadence at which to run the
            job.
        job : object
            Any object with attributes name, func, and cron. If specified,
            overrides the above three arguments.
        """
        if job is not None:
            if any([job_name, job_func, job_cron]):
                msg = "If job argument is set, all other arguments must not."
                raise ValueError(msg)
            job_name = job.name
            job_func = job.func
            job_cron = job.cron
        if job_name in self.jobdict:
            raise ValueError(f"Job name {job_name} already exists.")
        # Convert the current time to UTC so the math works.
        current_time = datetime.now().astimezone(pytz.utc)
        # Create a croniter object for the job.
        job_iter = croniter(job_cron, current_time, day_or=day_or)
        # Build a dictionary of one key, which we can use to update the master
        # jobdict.
        job = {
            job_name: {
                "func": job_func,
                "cron": job_cron,
                "iter": job_iter,
                "day_or": day_or,
                "next": job_iter.get_next(datetime),
            }
        }
        self.jobdict.update(job)

    def add_jobs(self, jobs, day_or=True):
        """
        Add multiple jobs at once.

        Just a convenience wrapper for add_job.

        Parameters
        ----------
        jobs : Iterable
            Iterable of objects, each of which has attributes name, func, and 
            cron.
        """
        for job in jobs:
            self.add_job(job=job)

    def run_pending(self):
        """
        Run all jobs whose next run is due to be kicked off.
        """
        for name, job in self.jobdict.items():
            # Execute any jobs that are due.
            if job["next"] < datetime.now().astimezone(pytz.utc):
                # Update the next time.
                job["next"] = job["iter"].get_next(datetime)
                # Then run the function.
                try:
                    job["func"]()
                # Catch *all* exceptions since the program should never die on
                # bad code in a job.
                except BaseException as e:
                    self.logger.error(str(e))

    def __str__(self):
        s = "<JobQueue with {} jobs>"
        s = s.format(len(self.jobdict))
        return s

    def __repr__(self):
        return f"JobQueue({repr(self.jobdict)})"
