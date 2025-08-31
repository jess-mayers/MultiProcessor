from ThreadPool import ThreadPool

def fn(i: int):
    import time
    time.sleep(i)
    return i

if __name__ == '__main__':
    import time
    import random
    pool = ThreadPool(max_workers=2, start=True)
    l = []
    for _ in range(10):
        i = random.randint(5,10)
        pool.submit(fn=fn, i=i)
        l.append(i)
    pool.done_submitting_tasks()
    results = list(pool.get_results())
    print(l)
    print(results)
    assert len(l) == len(results)
    x=1

