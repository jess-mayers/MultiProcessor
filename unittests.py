import os
import random
import unittest
from ThreadPool import ThreadPool
from collections import defaultdict


class EnsureAllProcessed(unittest.TestCase):
    def setUp(self):
        self.min_int_range = 1
        self.max_int_range = 10

        self.tasks_to_submit = 10

        self.result_to_count = defaultdict(int)
        self.pool = ThreadPool(max_workers=os.cpu_count())

    def test_validate_setup(self):
        assert self.min_int_range < self.max_int_range

    def test_submit_no_tasks(self):
        self.pool.done_submitting_tasks()
        results = list(self.pool.get_results())
        assert len(results) == 0

    def test_basic_addition(self):
        def add(a: int, b: int) -> int:
            return a+b

        for i in range(10):
            a = random.randint(self.min_int_range, self.max_int_range)
            b = random.randint(self.min_int_range,self.max_int_range)
            self.pool.submit(add, a=a, b=b)
            self.result_to_count[add(a=a,b=b)] += 1
        self.pool.done_submitting_tasks()
        results = list(self.pool.get_results())
        assert len(results) == self.tasks_to_submit
        for result, count in self.result_to_count.items():
            assert results.count(result) == count

    def test_basic_multiplication(self):
        def mult(a: int, b: int) -> int:
            return a*b

        for i in range(10):
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            self.pool.submit(mult, a=a, b=b)
        self.pool.done_submitting_tasks()
        results = list(self.pool.get_results())
        assert len(results) == self.tasks_to_submit
        for result, count in self.result_to_count.items():
            assert results.count(result) == count