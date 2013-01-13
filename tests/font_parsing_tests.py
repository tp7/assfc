import logging
import unittest
from functools import reduce
from ass_parser import StyleInfo, UsageData
from font_loader import TTFFont, FontInfo, FontLoader, TTCFont, FontWeight
from tests.common import get_file_in_test_directory

class FontLoaderTests(unittest.TestCase):
    def test_returns_all_not_found_fonts(self):
        loader = FontLoader(None, True)
        data = {StyleInfo('Jorvik', 0, False) : UsageData(), StyleInfo('Random font', 0, False) : UsageData()}
        found, not_found = loader.get_fonts_for_list(data)
        self.assertEqual(2, len(not_found))

    def test_returns_all_found_fonts(self):
        loader = FontLoader([get_file_in_test_directory('')], True)
        data = {StyleInfo('Jorvik Informal V2', 0, False) : UsageData(), StyleInfo('Random font', 0, False) : UsageData()}
        found, not_found = loader.get_fonts_for_list(data)
        self.assertEqual(1, len(found))
        self.assertIn('Jorvik Informal V2', list(found.values())[0].names)

    def test_performs_case_insensitive_search(self):
        loader = FontLoader([get_file_in_test_directory('')], True)
        data = {StyleInfo('JoRvIk INFormAl v2', 0, False) : UsageData()}
        found, not_found = loader.get_fonts_for_list(data)
        self.assertEqual(1, len(found))

    def test_does_not_add_same_font_twice(self):
        loader = FontLoader([get_file_in_test_directory(''), get_file_in_test_directory('')], True)
        data = {StyleInfo('Jorvik', 0, False) : UsageData(), StyleInfo('Jorvik informal', 0, False) : UsageData()}
        found, not_found = loader.get_fonts_for_list(data)
        self.assertEqual(1, len(found))

    def test_loads_at_least_some_system_fonts(self):
        loader = FontLoader(None, True)
        self.assertTrue(len(loader.fonts) > 0)

    def test_finds_all_required_fonts(self):
        loader = FontLoader(None, True)
        loader.fonts.append(FontInfo(['Arial'], False, False, FontWeight.FW_NORMAL, 'random', '1'))
        loader.fonts.append(FontInfo(['Arial Black'], False, False, FontWeight.FW_NORMAL, 'random', '2'))
        data = {StyleInfo('Arial', 0, False) : UsageData(), StyleInfo('Arial Black', 0, False) : UsageData()}
        found, not_found = loader.get_fonts_for_list(data)
        self.assertEqual(2, len(found))

    def test_returns_only_appropriate_font(self):
        loader = FontLoader(None, True)
        loader.fonts.append(FontInfo(['Arial'], False, False, FontWeight.FW_NORMAL, 'random', '1'))
        loader.fonts.append(FontInfo(['Arial Black'], False, False, FontWeight.FW_NORMAL, 'random', '2'))
        data = {StyleInfo('Arial', 0, False) : UsageData()}
        found, not_found = loader.get_fonts_for_list(data)
        self.assertEqual(1, len(found))

class TTFFontTests(unittest.TestCase):
    def test_ttf_name_matches(self):
        font = TTFFont(get_file_in_test_directory('seriously.ttf'))
        self.assertIn('Seriously', font.get_info().names)

    def test_otf_name_matches(self):
        font = TTFFont(get_file_in_test_directory('otfpoc.otf'))
        self.assertIn('otfpoc', font.get_info().names)

    def test_jorvik_v2_name_matches(self):
        font = TTFFont(get_file_in_test_directory('Jorvik.ttf'))
        self.assertIn('Jorvik Informal V2', font.get_info().names)

    def test_detects_italic_only_font(self):
        font = TTFFont(get_file_in_test_directory('CaviarDreams_Italic.ttf'))
        self.assertIs(font.get_info().italic, True)

    def test_detects_bold_only_font(self):
        font = TTFFont(get_file_in_test_directory('Caviar Dreams Bold.ttf'))
        self.assertIs(font.get_info().bold, True)

    def test_detects_italic_bold_font(self):
        font = TTFFont(get_file_in_test_directory('CaviarDreams_BoldItalic.ttf'))
        self.assertIs(font.get_info().italic, True)
        self.assertIs(font.get_info().bold, True)

    def test_parses_fonts_with_platform_id_2_strings(self):
        font = TTFFont(get_file_in_test_directory('VANTATHI.TTF'))
        self.assertIn('Vanta Thin', font.get_info().names)

    def test_parses_fonts_with_utf8_platform_id_0_strings(self):
        font = TTFFont(get_file_in_test_directory('SUSANNA_.otf'))
        self.assertIn('Susanna', font.get_info().names)

    def test_detects_bold_weight(self):
        font = TTFFont(get_file_in_test_directory('Caviar Dreams Bold.ttf'))
        self.assertEqual(font.get_info().weight, FontWeight.FW_BOLD)

    def test_detects_regular_weight(self):
        font = TTFFont(get_file_in_test_directory('Jorvik.ttf'))
        self.assertEqual(font.get_info().weight, FontWeight.FW_NORMAL)

    def test_detects_medium_weight(self):
        font = TTFFont(get_file_in_test_directory('seriously.ttf'))
        self.assertEqual(font.get_info().weight, FontWeight.FW_MEDIUM)

class TTCFontTests(unittest.TestCase):
    def test_contains_all_names(self):
        font = TTCFont(get_file_in_test_directory('jorvik_and_seriously.ttc'))
        self.assertIn('Seriously', reduce(lambda names, info: names + info.names, font.get_infos(), []))
        self.assertIn('Jorvik Informal V2', reduce(lambda names, info: names + info.names, font.get_infos(), []))

class FontInfoTests(unittest.TestCase):
    def test_calculates_md5_on_access(self):
        info = FontInfo([], False, False, 0, get_file_in_test_directory('Jorvik.ttf'), None)
        self.assertIsNotNone(info.md5)

    def test_calculates_correct_md5(self):
        info = FontInfo([], False, False, 0, get_file_in_test_directory('Jorvik.ttf'), None)
        self.assertEqual(info.md5, '0dae05c47e919281d7ac1e0170e4d3a8')

    def test_caches_md5_in_private_field(self):
        info = FontInfo([], False, False, 0, get_file_in_test_directory('Jorvik.ttf'), None)
        self.assertIsNone(info._FontInfo__md5)
        md5 = info.md5
        self.assertIsNotNone(info._FontInfo__md5)
