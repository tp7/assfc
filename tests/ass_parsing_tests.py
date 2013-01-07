import unittest
from ass_parser import AssParser
from tests.common import get_file_in_test_directory


class AssParsingTests(unittest.TestCase):
    def test_get_font_statistic_dev(self):
        stat = AssParser.get_fonts_statistics(get_file_in_test_directory('test1.ass'), True, True)

    def test_tags_parsing(self):
        blocks = AssParser.parse_tags(r"{\an5\blur1.1\fsp3\1a&H32\pos(962.2,918.8)}Animation number 392")

    def test_returns_correct_number_of_all_fonts_in_bakemono_script(self):
        parser = AssParser(get_file_in_test_directory('test1.ass'))
        self.assertEqual(len(parser.get_fonts(False, False)), 15)

    def test_returns_correct_number_of_all_fonts_in_bakemono_script_without_unused_styles(self):
        parser = AssParser(get_file_in_test_directory('test1.ass'))
        self.assertEqual(len(parser.get_fonts(True, False)), 14)

    def test_returns_correct_number_of_all_fonts_in_bakemono_script_without_comments(self):
        parser = AssParser(get_file_in_test_directory('test1.ass'))
        self.assertEqual(len(parser.get_fonts(False, True)), 14)

    def test_returns_correct_number_of_all_fonts_in_bakemono_script_without_unused_styles_and_comments(self):
        parser = AssParser(get_file_in_test_directory('test1.ass'))
        self.assertEqual(len(parser.get_fonts(True, True)), 13)

    def test_gets_correct_count_of_lines_font_used_in(self):
        parser = AssParser(get_file_in_test_directory('test1.ass'))
        self.assertEqual(len(parser.get_lines_font_used_in('YANEF')), 2)

    def test_gets_correct_count_of_lines_font_used_in_when_excluding_comment_lines(self):
        parser = AssParser(get_file_in_test_directory('test1.ass'))
        self.assertEqual(len(parser.get_lines_font_used_in('YANEF', True, True)), 1)

    def test_gets_correct_count_of_lines_style_used_in(self):
        parser = AssParser(get_file_in_test_directory('test1.ass'))
        self.assertEqual(len(parser.get_lines_style_used_in('Style with one comment and one dialogue line')), 2)

    def test_gets_correct_count_of_lines_style_used_in_when_excluding_comment_lines(self):
        parser = AssParser(get_file_in_test_directory('test1.ass'))
        self.assertEqual(len(parser.get_lines_style_used_in('Style with one comment and one dialogue line', True)), 1)
