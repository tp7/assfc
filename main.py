import logging
from ass_parser import AssParser
from font_loader import FontLoader
import os

logging.basicConfig(level = logging.DEBUG, format="LOG:%(levelname)s: %(message)s")

script_path = os.path.dirname(__file__) + "/content/test1.ass"
fonts_dirs = []

parser = AssParser(script_path)
collector = FontLoader(fonts_dirs)
found, not_found = collector.get_fonts_for_list(parser.get_fonts())
logging.debug('Total found: %i', len(found))
logging.debug('Total not found: %i', len(not_found))

