import logging
from multiprocessing import Lock

logger_lock = Lock()
# TODO memoria compartida entre todos los procesos, si se puede pasar a colas mejor

def initialize_log():
    """
    Python custom logging initialization
    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(component)s | %(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

class Logger:
    def __init__(self, component):
        self.extra = {'component': component}
    
    def info(self, message):
        with logger_lock:
            logging.info(message, extra=self.extra)
