"""Dispatch policy: priority first, then weighted fair share, then arrival order."""

from fractions import Fraction


class FairScheduler:
    def __init__(self, queue, weights=None):
        if weights is None:
            weights = {}
        if not isinstance(weights, dict):
            raise TypeError("weights must be a dict")
        for owner, weight in weights.items():
            if isinstance(weight, bool) or not isinstance(weight, int):
                raise TypeError("weight must be an int")
            if weight < 1:
                raise ValueError("weight must be at least 1")
        self._queue = queue
        self._weights = dict(weights)
        self._usage = {}

    def usage_of(self, owner):
        return self._usage.get(owner, 0)

    def usage(self):
        return dict(sorted(self._usage.items()))

    def _share(self, owner):
        return self._usage.get(owner, 0) // self._weights.get(owner, 1)

    def peek(self):
        pending = self._queue.pending()
        if not pending:
            return None
        top = max(job.priority for job in pending)
        candidates = [job for job in pending if job.priority == top]
        return min(candidates, key=lambda job: (self._share(job.owner), job.job_id))

    def next_job(self):
        job = self.peek()
        if job is None:
            return None
        self._queue.remove(job.job_id)
        self._usage[job.owner] = self._usage.get(job.owner, 0) + job.cost
        return job

    def drain(self):
        order = []
        while True:
            job = self.next_job()
            if job is None:
                return order
            order.append(job.job_id)
