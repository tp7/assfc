import os
import unittest
from ass_parser import AssParser
from font_loader import TTFFont


def get_file_in_test_directory(name):
    return os.path.dirname(__file__) + '/files/' + name

class AssParsingTests(unittest.TestCase):
    def test_count_of_fonts_in_bakemono_script_matches(self):
        parser = AssParser(get_file_in_test_directory('test1.ass'))
        self.assertEqual(len(parser.get_fonts()), 30)


class FontParsingTests(unittest.TestCase):
    def test_ttf_name_matches(self):
        font = TTFFont(get_file_in_test_directory('seriously.ttf'))
        self.assertIn('Seriously', font.get_names())

    def test_otf_name_matches(self):
        font = TTFFont(get_file_in_test_directory('otfpoc.otf'))
        self.assertIn('otfpoc', font.get_names())


if __name__ == '__main__':
    unittest.main(verbosity=2)

