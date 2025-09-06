import os
import random
import unittest
from ThreadPool import ThreadPool
from collections import defaultdict

# functions to test
def add(a: int, b: int) -> int:
    return a + b

def mult(a: int, b: int) -> int:
    return a * b

# unit test
class ThreadPoolUnitTest(unittest.TestCase):
    def setUp(self):
        # unit test config
        self.min_int_range = 1
        self.max_int_range = 10
        self.tasks_to_submit = 10
        # pool config
        self.max_workers = os.cpu_count()
        # used for validating the results
        self.result_to_count = defaultdict(int)
        # thread pool init
        self.pool = ThreadPool(max_workers=os.cpu_count())

    def test_validate_setup(self):
        assert self.max_workers > 0
        assert self.min_int_range < self.max_int_range

    def test_submit_no_tasks(self):
        self.pool.done_submitting_tasks()
        results = list(self.pool.get_results())
        assert len(results) == 0

    def test_addition(self):
        for i in range(self.tasks_to_submit):
            a = random.randint(self.min_int_range, self.max_int_range)
            b = random.randint(self.min_int_range,self.max_int_range)
            self.pool.submit(add, a=a, b=b)
            self.result_to_count[add(a=a,b=b)] += 1
        self.pool.done_submitting_tasks()
        results = list(self.pool.get_results())
        assert len(results) == self.tasks_to_submit
        for result, count in self.result_to_count.items():
            assert results.count(result) == count

    def test_multiplication(self):
        for i in range(self.tasks_to_submit):
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            self.pool.submit(mult, a=a, b=b)
        self.pool.done_submitting_tasks()
        results = list(self.pool.get_results())
        assert len(results) == self.tasks_to_submit
        for result, count in self.result_to_count.items():
            assert results.count(result) == count