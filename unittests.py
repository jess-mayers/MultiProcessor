import os
import unittest
from ThreadPool import ThreadPool

class EnsureAllProcessed(unittest.TestCase):
    def setUp(self):
        self.pool = ThreadPool(max_workers=os.cpu_count())

    def test_basic_addition(self):
        import random
        def add(a: int, b: int) -> int:
            return a+b

        tasks_to_submit = 10
        for i in range(10):
            self.pool.submit(add, a=random.randint(1, 10), b=random.randint(1,10))
        self.pool.done_submitting_tasks()

        assert len(list(self.pool.get_results())) == tasks_to_submit