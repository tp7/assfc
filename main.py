import logging
from time import ctime
from ass_parser import AssParser
from font_loader import FontLoader
import os
from json import JSONDecoder

class Config(object):
    def __init__(self, dict):
        self.__dict__.update(dict)

    def __repr__(self):
        return str(self.__dict__)

def get_script_directory():
    return os.path.dirname(__file__)

def parse_config():
    global config
    with open(get_script_directory() + "/config.json") as file:
        config = JSONDecoder(object_pairs_hook=Config).decode(file.read())

def set_logging(log_file):
    format = "LOG:%(levelname)s: %(message)s"
    logging.basicConfig(level = logging.DEBUG, format=format)

    if log_file:
        log_file = config.log_file if os.path.isabs(config.log_file) else "%s/%s" %(get_script_directory(), config.log_file)
        console = logging.FileHandler(log_file)
        console.setFormatter(logging.Formatter(format))
        logging.getLogger('').addHandler(console)

parse_config()
set_logging(config.log_file)


logging.info('-----Starting new task at %s-----' % str(ctime()))
script_path = get_script_directory() + "/content/test1.ass"


parser = AssParser(script_path)
collector = FontLoader(config.font_dirs)
found, not_found = collector.get_fonts_for_list(parser.get_fonts())
logging.debug('Total found: %i', len(found))
logging.debug('Total not found: %i', len(not_found))

