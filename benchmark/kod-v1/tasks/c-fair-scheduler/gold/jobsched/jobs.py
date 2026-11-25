"""Storage for pending jobs."""

from collections import namedtuple

Job = namedtuple("Job", "job_id owner priority cost seq")


def _check_name(value, label):
    if not isinstance(value, str):
        raise TypeError("%s must be a str" % label)
    if value == "":
        raise ValueError("%s must not be empty" % label)


def _check_int(value, label):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("%s must be an int" % label)


class JobQueue:
    def __init__(self):
        self._jobs = {}
        self._next_seq = 0

    def submit(self, job_id, owner, priority, cost):
        _check_name(job_id, "job_id")
        _check_name(owner, "owner")
        _check_int(priority, "priority")
        _check_int(cost, "cost")
        if cost < 1:
            raise ValueError("cost must be at least 1")
        if job_id in self._jobs:
            raise ValueError("duplicate pending job: %s" % job_id)
        seq = self._next_seq
        self._next_seq += 1
        self._jobs[job_id] = Job(job_id, owner, priority, cost, seq)
        return seq

    def remove(self, job_id):
        if job_id not in self._jobs:
            raise KeyError(job_id)
        return self._jobs.pop(job_id)

    def pending(self):
        return sorted(self._jobs.values(), key=lambda job: job.seq)

    def __len__(self):
        return len(self._jobs)

    def __contains__(self, job_id):
        return job_id in self._jobs
