from collections import defaultdict
import logging
import unittest
from ass_parser import AssParser, StyleInfo, UsageData
from tests.common import get_file_in_test_directory, disabled_logging

class StyleInfoTests(unittest.TestCase):
    def test_equals_returns_true_on_equal_items(self):
        info1 = StyleInfo('font', False, True)
        info2 = StyleInfo('font', False, True)
        self.assertEqual(info1, info2)

    def test_equals_returns_false_on_not_equal_items(self):
        info1 = StyleInfo('font', False, False)
        info2 = StyleInfo('font1', False, False)
        self.assertNotEqual(info1, info2)

    def test_hash_for_object_does_not_change(self):
        info1 = StyleInfo('font', False, True)
        self.assertEqual(hash(info1), hash(info1))

    def test_hash_differs_if_font_name_differs(self):
        info1 = StyleInfo('font', False, True)
        info2 = StyleInfo('font2', False, True)
        self.assertNotEqual(hash(info1), hash(info2))

    def test_hash_differs_if_any_of_styles_differ(self):
        info1 = StyleInfo('font', False, False)
        info2 = StyleInfo('font', True, False)
        info3 = StyleInfo('font', False, True)
        info4 = StyleInfo('font', True, True)
        self.assertNotEqual(hash(info1), hash(info2))
        self.assertNotEqual(hash(info1), hash(info3))
        self.assertNotEqual(hash(info1), hash(info4))
        self.assertNotEqual(hash(info2), hash(info3))
        self.assertNotEqual(hash(info2), hash(info4))
        self.assertNotEqual(hash(info3), hash(info4))

    def test_clone_returns_new_object(self):
        original = StyleInfo('font', False, False)
        new = original.clone()
        self.assertEqual(original, new)
        original.bold = True
        self.assertNotEqual(original, new)

    def test_from_ass_returns_compares_true_and_false_with_minus_one(self):
        item = StyleInfo.from_ass('font', '-123123123', '-1')
        self.assertTrue(item.italic)
        self.assertFalse(item.bold)

class AssBlockOverrideTests(unittest.TestCase):
    def test_does_not_include_blur(self):
        block = AssParser.AssBlockOverride(r'\blur12\fnFont\i1')
        with self.assertRaises(KeyError):
            tag = block.tags['b']

    def test_returns_correct_value_for_italic_and_bold_when_specified_as_a_single_digit(self):
        block = AssParser.AssBlockOverride(r'\blur12\b0\fnFont\i1')
        self.assertEqual(block.tags['i'], '1')
        self.assertEqual(block.tags['b'], '0')

    def test_returns_empty_string_when_italic_or_bold_does_not_have_digits(self):
        block = AssParser.AssBlockOverride(r'\blur12\b\fnFont\i')
        self.assertEqual(block.tags['i'], '')
        self.assertEqual(block.tags['b'], '')

    def test_detects_drawing(self):
        block = AssParser.AssBlockOverride(r'\blur1\p1\fnFont')
        self.assertEqual(block.tags['p'], '1')

    def test_parses_empty_style_override(self):
        block = AssParser.AssBlockOverride(r'\blur1\r\fnFont')
        self.assertEqual(block.tags['r'], '')

    def test_parses_style_override_with_style_name(self):
        block = AssParser.AssBlockOverride(r'\blur1\rRandom Style\fnFont')
        self.assertEqual(block.tags['r'], 'Random Style')

    def test_returns_correct_font_name_even_if_it_has_spaces(self):
        block = AssParser.AssBlockOverride(r'\blur12\b\fnFont with spaces\i')
        self.assertEqual(block.tags['fn'], 'Font with spaces')

    def test_returns_last_tag_value(self):
        block = AssParser.AssBlockOverride(r'\blur12\b1\fnFont\b0\i')
        self.assertEqual(block.tags['b'], '0')

    def test_returns_weight_for_bold_if_tag_has_multiple_digits(self):
        block = AssParser.AssBlockOverride(r'\blur12\b123\fnFont')
        self.assertEqual(block.tags['b'], '123')

    def test_get_tag_raises_key_error_if_tag_is_not_present(self):
        block = AssParser.AssBlockOverride('')
        with self.assertRaises(KeyError):
            value = block.get_tag('b', 12)

    def test_get_tag_returns_default_if_value_is_empty_string(self):
        block = AssParser.AssBlockOverride(r'\b\p1')
        self.assertEqual(block.get_tag('b', 12), 12)

    def test_get_tag_returns_value_if_it_exists(self):
        block = AssParser.AssBlockOverride(r'\b1\p1')
        self.assertTrue(block.get_tag('b', 12), 1)

class TagsParsingTests(unittest.TestCase):
    def test_returns_empty_list_on_empty_string(self):
        blocks = AssParser.parse_tags('')
        self.assertFalse(blocks)

    def test_returns_correct_number_of_blocks_but_does_not_include_uselss_ones(self):
        blocks = AssParser.parse_tags(r"{\an5\blur1.1\fsp3\1a&H32\pos(962.2,918.8)}Animation number 392")
        self.assertEqual(len(blocks), 1)

    def test_does_not_include_drawing(self):
        blocks = AssParser.parse_tags(r'{\b1\p1}blablabla{\p0}blablabla')
        self.assertEqual(len(blocks),3)

    def test_includes_tags_in_correct_order(self):
        blocks = AssParser.parse_tags(r'{\b1}blablabla{\b0}blablabla')
        self.assertIsInstance(blocks[0], AssParser.AssBlockOverride)
        self.assertIsInstance(blocks[1], AssParser.AssBlockPlain)
        self.assertIsInstance(blocks[2], AssParser.AssBlockOverride)
        self.assertIsInstance(blocks[3], AssParser.AssBlockPlain)

    def test_treats_not_closed_override_block_as_plain_text(self):
        with disabled_logging(logging.WARNING):
            blocks = AssParser.parse_tags(r'{\b1\b0blablabla')
        self.assertIsInstance(blocks[0], AssParser.AssBlockPlain)

    def does_not_include_comments(self):
        blocks = AssParser.parse_tags(r'{comment line}text')
        self.assertTrue(len(blocks),1)
        self.assertIsInstance(blocks[0], AssParser.AssBlockPlain)

    def does_not_include_completely_empty_override_blocks(self):
        blocks = AssParser.parse_tags(r'{}text')
        self.assertTrue(len(blocks),1)
        self.assertIsInstance(blocks[0], AssParser.AssBlockPlain)

class EventProcessingTests(unittest.TestCase):
    def test_find_all_unique_plain_text_characters(self):
        styles = {'style' : StyleInfo('Font', False, False)}
        used_styles = defaultdict(UsageData)
        event = AssParser.AssEvent(1, 'style','randommmm' ,False)
        AssParser.process_event(event, used_styles, styles)
        result = list(used_styles.values())[0]
        self.assertSequenceEqual({'r','a', 'n', 'd','o','m'}, result.chars)

    def test_also_includes_spaces(self):
        styles = {'style' : StyleInfo('Font', False, False)}
        used_styles = defaultdict(UsageData)
        event = AssParser.AssEvent(1, 'style','ra ndo mm mm' ,False)
        AssParser.process_event(event, used_styles, styles)
        result = list(used_styles.values())[0]
        self.assertSequenceEqual({'r','a', 'n', ' ', 'd','o','m'}, result.chars)

    def test_does_not_include_new_lines(self):
        styles = {'style' : StyleInfo('Font', False, False)}
        used_styles = defaultdict(UsageData)
        event = AssParser.AssEvent(1, 'style',r'rardo\nmm\Nmm' ,False)
        AssParser.process_event(event, used_styles, styles)
        result = list(used_styles.values())[0]
        self.assertSequenceEqual({'r','a', 'd','o','m'}, result.chars)

    def test_replaces_h_with_tab(self):
        styles = {'style' : StyleInfo('Font', False, False)}
        used_styles = defaultdict(UsageData)
        event = AssParser.AssEvent(1, 'style',r'lolol\hlolol' ,False)
        AssParser.process_event(event, used_styles, styles)
        result = list(used_styles.values())[0]
        self.assertSequenceEqual({'l','o', "\xA0"}, result.chars)

class AssParsingTests(unittest.TestCase):
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