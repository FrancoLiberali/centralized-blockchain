import logging
import logging.handlers
from multiprocessing import Process, Queue
import sys

def initialize_log():
    """
    Python custom logging initialization
    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(name)s | %(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

# based on https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes
# This is the listener process top-level loop: wait for logging events
# (LogRecords) on the queue and handle them, quit when you get a None for a
# LogRecord.
def listener_process(queue):
    initialize_log()
    while True:
        try:
            record = queue.get()
            if record is None:  # We send this as a sentinel to tell the listener to quit.
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)
        except Exception:
            import traceback
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def configure_log():
    log_queue = Queue()
    log_listener = Process(target=listener_process,
                           args=(log_queue,))
    log_listener.start()

    h = logging.handlers.QueueHandler(log_queue)  # Just the one handler needed
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.INFO)
    return log_queue, log_listener


def join_logger(log_queue, log_listener):
    log_queue.put_nowait(None)
    log_listener.join()
