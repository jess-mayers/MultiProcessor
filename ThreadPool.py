import os
import uuid
import traceback
import threading
from queue import Queue, Empty
from typing import Callable, List
from exceptions import AlreadyTerminatedException, ThreadException

class PoolTask:
    def __init__(self, task_id: uuid.UUID, fn: Callable, *args, **kwargs):
        self.task_id = task_id
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def execute(self):
        return self.fn(*self.args, **self.kwargs)

class ThreadPool:
    def __init__(self, max_workers: int = os.cpu_count(), start: bool = False):
        # config
        assert max_workers and max_workers > 0, 'max_workers must be greater than 0'
        # events
        self.__start_event = threading.Event()
        # run states
        self.__terminated = False
        if start:
            self.start()
        # task handling
        self.submitted_one_job = False
        self.finished_one_job = False
        self.still_submitting = True
        self.input_queue = Queue()
        self.output_queue = Queue()

        # create thread pool
        self.pool : List[threading.Thread] = []
        for i in range(max_workers):
            thread = threading.Thread(target=self.__thread_worker, daemon=True)
            thread.start()
            self.pool.append(thread)

    def start(self):
        self.__start_event.set()

    def done_submitting_tasks(self):
        self.still_submitting = False

    def submit(self, fn: Callable, *args, **kwargs):
        task_id = uuid.uuid4()
        task = PoolTask(task_id=task_id, fn=fn, *args, **kwargs)
        self.input_queue.put(task)
        self.submitted_one_job = True

    def __thread_worker(self):
        # thread code
        while not self.input_queue.empty() or self.still_submitting:
            if self.__terminated:
                # end process
                return
            # wait for start
            self.__start_event.wait()
            # get next item in queue
            try:
                task = self.input_queue.get(timeout=10)
            except Empty:
                # no task appeared in 10 seconds check to ensure system is fully running
                continue
            # process results
            try:
                # put result into queue
                self.output_queue.put(task.execute())
            except Exception:
                # exception occurred in thread return thread exception
                self.output_queue.put(ThreadException(traceback.format_exc()))
            # mark task as done
            self.input_queue.task_done()
            self.finished_one_job = True

    def terminate(self, force: bool = False):
        if self.__terminated:
            raise AlreadyTerminatedException('Cannot terminate a threadpool that is already terminated')
        if force:
            # todo force end all threads
            pass
        self.__terminated = True

    def get_results(self, timeout: int = 10, raise_thread_errors: bool = True):
        assert self.submitted_one_job, 'A job needs to be submitted'
        # TODO fix condition to get results
        while not self.finished_one_job or self.still_submitting or not self.input_queue.all_tasks_done or self.output_queue.not_empty:
            try:
                result = self.output_queue.get(timeout=timeout)
                self.output_queue.task_done()
                if raise_thread_errors and isinstance(result, ThreadException):
                    raise result
                yield result
            except Empty:
                continue
        self.terminate()
