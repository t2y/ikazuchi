# -*- coding: utf-8 -*-

import threading

_MAX_SEMAPHORE = 10

def call_api_with_multithread(api_method, target_lines):
    def worker(line, results, i, semaphore):
        with semaphore:
            results[i] = api_method(line)

    results = []
    s = threading.Semaphore(_MAX_SEMAPHORE)
    for i, line in enumerate(target_lines):
        results.append(None)
        t = threading.Thread(target=worker, args=(line, results, i, s))
        t.start()
    # waiting for threads to complete
    main_thread = threading.currentThread()
    for t in threading.enumerate():
        if t is not main_thread:
            t.join()
    return results
