import unittest
from ass_parser import AssParser
from tests.common import get_file_in_test_directory


class AssParsingTests(unittest.TestCase):
    def test_count_of_fonts_in_bakemono_script_matches(self):
        parser = AssParser(get_file_in_test_directory('test1.ass'))
        self.assertEqual(len(parser.get_fonts()), 30)
