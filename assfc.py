import argparse
import logging
from time import ctime
import sys
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

def create_mmg_command(mmg_path, output_path, script_path, fonts):
    font_list = ('--attachment-mime-type application/x-truetype-font --attachment-name "{0}" --attach-file "{1}"'.format(os.path.basename(font.path), font.path) for font in fonts)
    attachment_string = ' '.join(font_list)
    return '{0} -o "{1}" "{2}" {4}'.format(os.path.abspath(mmg_path), os.path.abspath(output_path), os.path.abspath(script_path), attachment_string)


def process(args):
    parse_config()
    set_logging(config.log_file)
    logging.info('-----Started new task at %s-----' % str(ctime()))

    parser = AssParser(os.path.abspath(args.script))
    collector = FontLoader(config.font_dirs)

    found, not_found = collector.get_fonts_for_list(parser.fonts)

    logging.info('Total found: %i', len(found))
    logging.info('Total not found: %i', len(not_found))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ASS font collector")
    parser.add_argument('-o', default=None, dest='output_folder', metavar='folder', help='output folder', required=True)
    parser.add_argument('-v','--verbose', action='store_true', dest='verbose', help='show current frame')
    parser.add_argument('script', default=None, help='input script')
    args = parser.parse_args(sys.argv[1:])
    process(args)

