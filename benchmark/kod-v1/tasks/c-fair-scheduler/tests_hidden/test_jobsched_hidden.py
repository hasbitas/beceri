import unittest

from jobsched import FairScheduler, Job, JobQueue


class HiddenTests(unittest.TestCase):
    def test_weights_use_exact_ratios(self):
        queue = JobQueue()
        for number in range(1, 4):
            queue.submit("a%d" % number, "a", 0, 3)
        for number in range(1, 4):
            queue.submit("b%d" % number, "b", 0, 3)
        scheduler = FairScheduler(queue, weights={"a": 2, "b": 3})
        self.assertEqual(scheduler.drain(), ["a1", "b1", "b2", "a2", "b3", "a3"])
        self.assertEqual(scheduler.usage(), {"a": 9, "b": 9})

    def test_equal_share_ties_go_to_earliest_submission_not_smallest_id(self):
        queue = JobQueue()
        queue.submit("zulu", "o1", 0, 1)
        queue.submit("alpha", "o2", 0, 1)
        queue.submit("mike", "o1", 0, 1)
        scheduler = FairScheduler(queue)
        self.assertEqual(scheduler.next_job().job_id, "zulu")
        self.assertEqual(scheduler.next_job().job_id, "alpha")
        self.assertEqual(scheduler.next_job().job_id, "mike")

    def test_priority_beats_fair_share(self):
        queue = JobQueue()
        queue.submit("low-1", "light", 1, 1)
        queue.submit("hot-1", "heavy", 9, 50)
        queue.submit("hot-2", "heavy", 9, 50)
        queue.submit("low-2", "light", 1, 1)
        scheduler = FairScheduler(queue)
        self.assertEqual(scheduler.drain(), ["hot-1", "hot-2", "low-1", "low-2"])
        queue.submit("late-heavy", "heavy", 1, 1)
        queue.submit("late-light", "light", 1, 1)
        self.assertEqual(scheduler.drain(), ["late-light", "late-heavy"])

    def test_negative_priorities_and_usage_persist(self):
        queue = JobQueue()
        queue.submit("n1", "p", -5, 4)
        queue.submit("n2", "q", -1, 1)
        scheduler = FairScheduler(queue)
        self.assertEqual(scheduler.next_job().job_id, "n2")
        self.assertEqual(scheduler.next_job().job_id, "n1")
        self.assertIsNone(scheduler.next_job())
        self.assertEqual(scheduler.usage_of("p"), 4)
        self.assertEqual(scheduler.usage_of("nobody"), 0)
        queue.submit("n3", "p", 0, 1)
        queue.submit("n4", "q", 0, 1)
        self.assertEqual(scheduler.drain(), ["n4", "n3"])

    def test_removed_jobs_are_skipped_and_resubmission_goes_last(self):
        queue = JobQueue()
        self.assertEqual(queue.submit("a", "o", 0, 1), 0)
        self.assertEqual(queue.submit("b", "o", 0, 1), 1)
        self.assertEqual(queue.submit("c", "o", 0, 1), 2)
        removed = queue.remove("a")
        self.assertEqual(removed, Job("a", "o", 0, 1, 0))
        self.assertEqual(queue.submit("a", "o", 0, 1), 3)
        self.assertEqual([job.job_id for job in queue.pending()], ["b", "c", "a"])
        with self.assertRaises(KeyError):
            queue.remove("zzz")
        self.assertEqual(FairScheduler(queue).drain(), ["b", "c", "a"])

    def test_peek_does_not_change_anything(self):
        queue = JobQueue()
        scheduler = FairScheduler(queue)
        self.assertIsNone(scheduler.peek())
        self.assertIsNone(scheduler.next_job())
        self.assertEqual(scheduler.drain(), [])
        queue.submit("k", "o", 2, 7)
        first = scheduler.peek()
        self.assertEqual(first, scheduler.peek())
        self.assertEqual(len(queue), 1)
        self.assertEqual(scheduler.usage(), {})
        self.assertEqual(scheduler.next_job(), first)
        self.assertEqual(scheduler.usage(), {"o": 7})

    def test_submit_validation_order_and_atomicity(self):
        queue = JobQueue()
        queue.submit("dup", "o", 0, 1)
        cases = (
            (("", 5, 1.5, 0), ValueError),
            ((3, "", True, 0), TypeError),
            (("j", 4, 0, 1), TypeError),
            (("j", "", 0, 1), ValueError),
            (("j", "o", True, 1), TypeError),
            (("j", "o", 1.0, 1), TypeError),
            (("j", "o", 0, False), TypeError),
            (("j", "o", 0, 0), ValueError),
            (("j", "o", 0, -3), ValueError),
            (("dup", "o", 0, 0), ValueError),
            (("dup", "o", 0, "x"), TypeError),
        )
        for args, error in cases:
            with self.assertRaises(error, msg=repr(args)):
                queue.submit(*args)
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue.submit("fresh", "o", 0, 1), 1)
        self.assertNotIn("j", queue)

    def test_weight_validation_and_isolation(self):
        queue = JobQueue()
        with self.assertRaises(TypeError):
            FairScheduler(queue, weights=[1])
        with self.assertRaises(TypeError):
            FairScheduler(queue, weights={"a": 1.5})
        with self.assertRaises(TypeError):
            FairScheduler(queue, weights={"a": True})
        with self.assertRaises(ValueError):
            FairScheduler(queue, weights={"a": 0})
        weights = {"a": 2}
        scheduler = FairScheduler(queue, weights=weights)
        weights["a"] = 1000
        queue.submit("a1", "a", 0, 4)
        queue.submit("b1", "b", 0, 1)
        queue.submit("a2", "a", 0, 4)
        queue.submit("b2", "b", 0, 1)
        self.assertEqual(scheduler.drain(), ["a1", "b1", "b2", "a2"])

    def test_usage_report_is_sorted_copy(self):
        queue = JobQueue()
        queue.submit("1", "zed", 0, 2)
        queue.submit("2", "amy", 0, 3)
        scheduler = FairScheduler(queue)
        scheduler.drain()
        report = scheduler.usage()
        self.assertEqual(list(report.items()), [("amy", 3), ("zed", 2)])
        report["amy"] = 99
        self.assertEqual(scheduler.usage_of("amy"), 3)


if __name__ == "__main__":
    unittest.main()
