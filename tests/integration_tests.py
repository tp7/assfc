import logging
import unittest
from ass_parser import AssParser
from font_loader import FontLoader
from font_loader.ttf_parser import TTFFont
from tests.common import get_file_in_test_directory


class IntegrationTests(unittest.TestCase):
    @unittest.skip
    def test_correctly_finds_yanone_kaffeesatz_bold(self):
        logging.basicConfig(level=logging.DEBUG)

        f = TTFFont(get_file_in_test_directory('YanoneKaffeesatz-Bold.otf'))
        f.print_headers()

        stat = AssParser.get_fonts_statistics(get_file_in_test_directory('3.ass'), True, True)
        loader = FontLoader([get_file_in_test_directory('')])
        found, not_found = loader.get_fonts_for_list(stat)
        self.assertFalse(not_found)

        logging.disable(logging.DEBUG)