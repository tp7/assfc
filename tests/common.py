import os

def get_file_in_test_directory(name):
    return os.path.join(os.path.dirname(__file__), 'files', name)
