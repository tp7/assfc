import unittest
from ass_parser import AssParser
from tests.common import get_file_in_test_directory


class AssParsingTests(unittest.TestCase):
    def test_returns_correct_number_of_blocks(self):
        blocks = AssParser.parse_tags(r"{\an5\blur1.1\fsp3\1a&H32\pos(962.2,918.8)}Animation number 392")
        self.assertEqual(len(blocks), 2)

    def test_returns_correct_number_of_all_fonts_in_bakemono_script(self):
        stat = AssParser.get_fonts_statistics(get_file_in_test_directory('test1.ass'), False, False)
        self.assertEqual(len(stat), 19)

    def test_returns_correct_number_of_all_fonts_in_bakemono_script_without_unused_styles(self):
        stat = AssParser.get_fonts_statistics(get_file_in_test_directory('test1.ass'), True, False)
        self.assertEqual(len(stat), 18)

    def test_returns_correct_number_of_all_fonts_in_bakemono_script_without_comments(self):
        stat = AssParser.get_fonts_statistics(get_file_in_test_directory('test1.ass'), False, True)
        self.assertEqual(len(stat), 18)

    def test_returns_correct_number_of_all_fonts_in_bakemono_script_without_unused_styles_and_comments(self):
        stat = AssParser.get_fonts_statistics(get_file_in_test_directory('test1.ass'), True, True)
        self.assertEqual(len(stat), 17)

    def test_gets_correct_count_of_styles_font_used_in(self):
        stat = AssParser.get_fonts_statistics(get_file_in_test_directory('test1.ass'), True, True)
        for key, value in stat.items():
            if key.fontname == 'YANEF':
                found = value
        self.assertEqual(len(found.styles), 1)

    def gets_correct_count_of_lines_font_used_in(self):
        stat = AssParser.get_fonts_statistics(get_file_in_test_directory('test1.ass'), False, False)
        for key, value in stat.items():
            if key.fontname == 'this is totally not real font':
                found = value
        self.assertEqual(len(found.lines), 1)