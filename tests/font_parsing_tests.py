import unittest
from font_loader import TTFFont, FontInfo
from tests.common import get_file_in_test_directory

class FontParsingTests(unittest.TestCase):
    def test_ttf_name_matches(self):
        font = TTFFont(get_file_in_test_directory('seriously.ttf'))
        self.assertIn('Seriously', font.get_names())

    def test_otf_name_matches(self):
        font = TTFFont(get_file_in_test_directory('otfpoc.otf'))
        self.assertIn('otfpoc', font.get_names())

    def test_jorvik_v2_name_matches(self):
        font = TTFFont(get_file_in_test_directory('Jorvik.ttf'))
        self.assertIn('Jorvik Informal V2', font.get_names())

    def test_detects_italic_only_font(self):
        font = TTFFont(get_file_in_test_directory('CaviarDreams_Italic.ttf'))
        self.assertTrue(font.is_italic())
        self.assertFalse(font.is_bold())

    def test_detects_bold_only_font(self):
        font = TTFFont(get_file_in_test_directory('Caviar Dreams Bold.ttf'))
        self.assertTrue(font.is_bold())
        self.assertFalse(font.is_italic())

    def test_detects_italic_bold_font(self):
        font = TTFFont(get_file_in_test_directory('CaviarDreams_BoldItalic.ttf'))
        self.assertTrue(font.is_italic())
        self.assertTrue(font.is_bold())


class FontInfoTests(unittest.TestCase):
    def test_calculates_md5_on_access(self):
        info = FontInfo([], [], get_file_in_test_directory('Jorvik.ttf'), None)
        self.assertIsNotNone(info.md5)

    def test_calculates_correct_md5(self):
        info = FontInfo([], [], get_file_in_test_directory('Jorvik.ttf'), None)
        self.assertEqual(info.md5, '0dae05c47e919281d7ac1e0170e4d3a8')

    def test_caches_md5_in_private_field(self):
        info = FontInfo([], [], get_file_in_test_directory('Jorvik.ttf'), None)
        self.assertIsNone(info._FontInfo__md5)
        md5 = info.md5
        self.assertIsNotNone(info._FontInfo__md5)
