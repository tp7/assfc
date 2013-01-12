from contextlib import contextmanager
import logging
import os

def get_file_in_test_directory(name):
    return os.path.join(os.path.dirname(__file__), 'files', name)



class disabled_logging():
    def __init__(self, level):
        self.level = level

    def __enter__(self):
        logging.disable(self.level)

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.disable(logging.NOTSET)
