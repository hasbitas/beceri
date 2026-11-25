import unittest

from jobsched import FairScheduler, Job, JobQueue


class VisibleTests(unittest.TestCase):
    def test_priority_then_arrival_order(self):
        queue = JobQueue()
        queue.submit("j1", "ann", 1, 1)
        queue.submit("j2", "ann", 5, 1)
        queue.submit("j3", "ann", 5, 1)
        queue.submit("j4", "ann", 3, 1)
        self.assertEqual(FairScheduler(queue).drain(), ["j2", "j3", "j4", "j1"])
        self.assertEqual(len(queue), 0)

    def test_owners_share_fairly_at_equal_priority(self):
        queue = JobQueue()
        for number in range(1, 4):
            queue.submit("a%d" % number, "ann", 1, 2)
        queue.submit("b1", "bob", 1, 3)
        queue.submit("b2", "bob", 1, 3)
        scheduler = FairScheduler(queue)
        self.assertEqual(scheduler.drain(), ["a1", "b1", "a2", "b2", "a3"])
        self.assertEqual(scheduler.usage(), {"ann": 6, "bob": 6})

    def test_job_ids_can_be_reused_after_dispatch_or_removal(self):
        queue = JobQueue()
        queue.submit("x", "ann", 0, 1)
        with self.assertRaises(ValueError):
            queue.submit("x", "bob", 0, 1)
        scheduler = FairScheduler(queue)
        self.assertEqual(scheduler.next_job().job_id, "x")
        queue.submit("x", "bob", 0, 1)
        self.assertEqual(queue.remove("x").owner, "bob")
        queue.submit("x", "cyd", 0, 1)
        self.assertIn("x", queue)
        self.assertEqual(queue.pending(), [Job("x", "cyd", 0, 1, 2)])


if __name__ == "__main__":
    unittest.main()
