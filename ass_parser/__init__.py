from collections import namedtuple, defaultdict
import logging
from re import compile
import sys


class StyleInfo(object):
    __slots__ = ['fontname', 'bold', 'italic']

    def __init__(self, fontname, bold, italic):
        self.fontname = fontname
        self.bold = bold
        self.italic = italic

    def __repr__(self):
        return '%s (Bold: %s, Italic: %s)' % (self.fontname, str(self.bold), str(self.italic))

    def __hash__(self):
        return hash((self.fontname.lower(), self.bold, self.italic))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def clone(self):
        return StyleInfo(self.fontname, self.bold, self.italic)

    @staticmethod
    def from_ass(fontname, weight, italic):
        return StyleInfo(fontname, 0 if weight == '0' else 1 if weight == '-1' else int(weight), italic == '-1')

class UsageData(object):
    #styles refer to ASS styles defined globally
    __slots__ = ['lines', 'styles', 'chars']

    def __init__(self):
        self.lines = set()
        self.styles = set()
        self.chars = set()

    def __repr__(self):
        lines = list(self.lines)
        lines.sort()
        return 'Styles: %s, lines: %s' % (self.styles, lines)

class AssParser(object):
    AssEvent = namedtuple('AssEvent', ['line_number', 'style', 'text', 'is_comment'] )
    AssBlockPlain = namedtuple('AssBlockPlain', ['text'])

    class AssBlockOverride(object):
        __slots__ = ['tags']

        tag_regex = compile(r'\\(i(?=[\d\\]|$)|b(?=[\d\\]|$)|fn|r|p(?=\d))((?<![ibp])[^\\]*|\d*)')

        def __init__(self, text):
            self.tags = {f[0].lower():f[1] for f in self.tag_regex.findall(text)}

        def __repr__(self):
            return 'OverrideBlock(text=%s)' %  ''.join(('\\%s%s' %(name, value) for name, value in self.tags.items()))

        def get_tag(self, name, default):
            value = self.tags[name]
            if value is None or value == '':
                return default
            return value

#    Style format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut,
#                   ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding

#    Event format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

    @staticmethod
    def get_fonts_statistics(path, exclude_unused_fonts = False, exclude_comments = False):
        try:
            styles, events = AssParser.read_script(path)
        except Exception as e:
            logging.critical('Failed to parse script %s: %s' % (path, e))
            sys.exit(1)
        used_styles = defaultdict(UsageData)

        for name, info in styles.items():
            used_styles[info].styles.add(name)

        for event in events:
            if exclude_comments and event.is_comment:
                continue
            AssParser.process_event(event, used_styles, styles)

        if exclude_unused_fonts:
            for info, usage in  list(used_styles.items()):
                if not usage.chars:
                    del used_styles[info]

        return used_styles


    @staticmethod
    def process_event(event, used_styles, styles):
        blocks = AssParser.parse_tags(event.text)
        style = styles[event.style].clone()
        initial = style.clone()
        overriden = False
        for block in blocks:
            try:
                #if isinstance(block, AssParser.AssBlockOverride):
                if 'r' in block.tags:
                    style = styles[block.get_tag('r', event.style)].clone()
                    overriden = False
                if 'b' in block.tags:
                    value = block.get_tag('b', initial.bold)
                    bold = 0 if value == '0' else 1 if value == '1' else int(value)
                    style = StyleInfo(style.fontname, bold, style.italic)
                    overriden = True
                if 'i' in block.tags:
                    style = StyleInfo(style.fontname, style.bold, bool(int(block.get_tag('i', initial.italic))))
                    overriden = True
                if 'fn' in block.tags:
                    style = StyleInfo(block.get_tag('fn', initial.fontname), style.bold, style.italic)
                    overriden = True
            except AttributeError: #AssParser.AssBlockPlain
                if not block.text:
                    continue

                used_style = used_styles[style]
                if overriden:
                    used_style.lines.add(event.line_number)

                str = block.text.replace(r'\n','').replace(r'\N','').replace(r'\h', "\xA0")
                used_style.chars.update(str)


    @staticmethod
    def parse_tags(text):
        if not text:
            return []

        blocks = []
        drawing = False
        cur = 0
        strlen = len(text)
        #todo: this whole thing is way too C++
        while cur < strlen:
            if text[cur] == '{':
                end = text.find('}', cur)
                if end == -1:
                    logging.warning('Broken line: %s' % text)
                    cur = AssParser.process_plain_text(blocks, text, cur, drawing)
                else:
                    cur, drawing = AssParser.process_override_block(blocks, text, cur, end, drawing)
            else:
                cur = AssParser.process_plain_text(blocks, text, cur, drawing)

        return blocks


    @staticmethod
    def process_override_block(blocks, text, pos, end, drawing):
        work = text[pos+1:end]
        if not '\\' in work:
            #comment line - do nothing
            pass
        else:
            block = AssParser.AssBlockOverride(work)
            if not block.tags:
                return end+1, drawing
            blocks.append(block)
            try:
                drawing = block.tags['p'] != '0'
            except KeyError:
                pass
        return end+1, drawing

    @staticmethod
    def process_plain_text(blocks, text, pos, drawing):
        end = text.find('{', pos+1)
        if end == -1:
            work = text[pos:]
            pos = len(text)
        else:
            work = text[pos:end]
            pos = end
        if drawing:
            pass
        else:
            blocks.append(AssParser.AssBlockPlain(work))
        return pos

    @staticmethod
    def read_script(path):
        try:
            with open(path, encoding='utf-8') as file:
                script = file.read()
        except IOError:
            logging.critical("Script at path %s wasn't found" % path)
            sys.exit(2)
        styles = {}
        events = []
        idx = 1
        for line in script.splitlines():
            try:
                descriptor, value = line.split(':', 1)
            except ValueError:
                continue
            if descriptor not in {'Dialogue', 'Comment', 'Style'}:
                continue
            if descriptor in {'Dialogue', 'Comment'}:
                event = value.split(',', 9) #len(EventFormat) - 1
                ass_event = AssParser.AssEvent(idx, event[3], event[9].strip(), True if descriptor=='Comment' else False)
                idx += 1
                events.append(ass_event)
            else:
                ass_style = value.split(',', 22) #len(AssParser.EventFormat) - 1
                style_info = StyleInfo.from_ass(ass_style[1], ass_style[7], ass_style[8])#
                styles[ass_style[0].strip()] = style_info
        return styles, events
