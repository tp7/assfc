import logging
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


config = None
logging.basicConfig(level = logging.DEBUG, format="LOG:%(levelname)s: %(message)s")
script_path = get_script_directory() + "/content/test1.ass"
parse_config()

parser = AssParser(script_path)
collector = FontLoader(config.font_dirs)
found, not_found = collector.get_fonts_for_list(parser.get_fonts())
logging.debug('Total found: %i', len(found))
logging.debug('Total not found: %i', len(not_found))
