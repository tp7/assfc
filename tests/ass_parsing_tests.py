import unittest
from ass_parser import AssParser
from tests.common import get_file_in_test_directory


class AssParsingTests(unittest.TestCase):
    def test_returns_correct_number_of_all_fonts_in_bakemono_script(self):
        parser = AssParser(get_file_in_test_directory('test1.ass'))
        self.assertEqual(len(parser.get_fonts(False, False)), 14)

    def test_returns_correct_number_of_all_fonts_in_bakemono_script_without_unused_styles(self):
        parser = AssParser(get_file_in_test_directory('test1.ass'))
        self.assertEqual(len(parser.get_fonts(True, False)), 13)

    def test_returns_correct_number_of_all_fonts_in_bakemono_script_without_comments(self):
        parser = AssParser(get_file_in_test_directory('test1.ass'))
        self.assertEqual(len(parser.get_fonts(False, True)), 13)

    def test_returns_correct_number_of_all_fonts_in_bakemono_script_without_unused_styles_and_comments(self):
        parser = AssParser(get_file_in_test_directory('test1.ass'))
        self.assertEqual(len(parser.get_fonts(True, True)), 12)
