import os
import random
import unittest
from ThreadPool import ThreadPool

# functions to test
def add(a: int, b: int) -> int:
    return a + b

def mult(a: int, b: int) -> int:
    return a * b

# unit test
class ThreadPoolUnitTest(unittest.TestCase):
    def setUp(self):
        # unit test config
        self.tasks_to_submit = 10
        self.max_workers = os.cpu_count()
        # thread pool init
        self.pool = ThreadPool(max_workers=os.cpu_count())

    def validate_expected(self, results: list):
        assert len(results) == self.tasks_to_submit

    def test_validate_config(self):
        # validate configs in setup
        assert self.max_workers > 0
        assert self.tasks_to_submit > 0

    def test_submit_no_tasks(self):
        self.pool.done_submitting_tasks()
        results = list(self.pool.get_results())
        assert len(results) == 0

    def test_addition(self):
        # test config
        min_int_range = 10
        max_int_range = 1000
        assert min_int_range < max_int_range, 'Min range must be less than Max range'

        for _ in range(self.tasks_to_submit):
            a = random.randint(min_int_range, max_int_range)
            b = random.randint(min_int_range, max_int_range)
            self.pool.submit(add, a=a, b=b)
        self.pool.done_submitting_tasks()
        results = list(self.pool.get_results())
        self.validate_expected(results)

    def test_multiplication(self):
        # test config
        min_int_range = 10
        max_int_range = 1000
        assert min_int_range < max_int_range, 'Min range must be less than Max range'

        for _ in range(self.tasks_to_submit):
            a = random.randint(min_int_range, max_int_range)
            b = random.randint(min_int_range, max_int_range)
            self.pool.submit(mult, a=a, b=b)
        self.pool.done_submitting_tasks()
        results = list(self.pool.get_results())
        self.validate_expected(results)