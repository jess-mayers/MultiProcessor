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

class WorkerThread(threading.Thread):
    def __init__(self, target: Callable, auto_start: bool = True, *args, **kwargs):
        super().__init__(target=target, daemon=True, *args, **kwargs)
        self._stop_event = threading.Event()
        if auto_start:
            self.start()
    def stop(self):
        self._stop_event.set()
    def is_stopped(self):
        return self._stop_event.is_set()

class ThreadPool:
    def __init__(self, max_workers: int = os.cpu_count()):
        # config
        assert max_workers and max_workers > 0, 'max_workers must be greater than 0'
        # run states
        self.__terminated = False
        # task handling
        self.still_submitting = True
        self.still_processing = True
        self.input_queue = Queue()
        self.output_queue = Queue()
        # task tracking
        self.__tasks_submitted = 0
        self.__tasks_completed = 0
        self.__task_errors = 0

        # create thread pool
        self.pool: List[WorkerThread] = []
        for i in range(max_workers):
            self.pool.append(WorkerThread(target=self.__thread_worker, auto_start=True))

    def done_submitting_tasks(self):
        self.still_submitting = False

    def submit(self, fn: Callable, *args, **kwargs):
        task_id = uuid.uuid4()
        task = PoolTask(task_id=task_id, fn=fn, *args, **kwargs)
        self.input_queue.put_nowait(task)
        self.__tasks_submitted += 1

    def __thread_worker(self):
        # thread code
        while self.still_submitting or not self.input_queue.empty():
            if self.__terminated:
                # end thread
                return
            # get next item in queue
            try:
                task = self.input_queue.get(timeout=10)
            except Empty:
                # no task appeared in 10 seconds check to ensure system is fully running
                continue
            # process results
            try:
                # put result into queue
                result = task.execute()
            except Exception:
                # exception occurred in thread return thread exception
                result = ThreadException(traceback.format_exc())
                self.__task_errors += 1
            self.output_queue.put(result)
            # mark task as done
            self.input_queue.task_done()
        self.still_processing = False

    def terminate(self, force: bool = False):
        if self.__terminated:
            raise AlreadyTerminatedException('Cannot terminate a threadpool that is already terminated')
        if force:
            for worker in self.pool:
                # force stop all threads
                worker.stop()
        self.__terminated = True

    def get_results(self, timeout: int = 10, raise_thread_errors: bool = True):
        while self.still_submitting or self.still_processing or not self.output_queue.empty():
            try:
                result = self.output_queue.get(timeout=timeout)
                self.output_queue.task_done()
                if raise_thread_errors and isinstance(result, ThreadException):
                    raise result
                yield result
                self.__tasks_completed += 1
            except Empty:
                continue