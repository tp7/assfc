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
        return hash('%s%i%i' % (self.fontname.lower(), int(self.bold), int(self.italic)))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def clone(self):
        return StyleInfo(self.fontname, self.bold, self.italic)

    @staticmethod
    def from_ass(fontname, bold, italic):
        return StyleInfo(fontname, bold == '-1', italic == '-1')

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

    class AssTag(object):
        __slots__ = ['name', 'value']
        def __init__(self, name, value):
            self.name = name
            self.value = value

        def get_value(self, default):
            if self.value is None or self.value == '':
                return default
            return self.value

    class AssBlockOverride(object):
        __slots__ = ['tags']

        tag_regex = compile(r'\\(i(?=[\d\\]|$)|b(?=[\d\\]|$)|fn|r|p(?=\d))((?<![ibp])[^\\]*|\d*)')

        def __init__(self, text):
            self.tags = [AssParser.AssTag(f[0], f[1]) for f in self.tag_regex.findall(text)]

        def __repr__(self):
            return 'OverrideBlock(text=%s)' %  ''.join(('\\%s%s' %(tag.name, tag.value) for tag in self.tags))

        def get_tag(self, name):
            tags = list(self.tags)
            tags.reverse()
            for tag in tags:
                if tag.name == name:
                    return tag
            return None

#    Style format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut,
#                   ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding

#    Event format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

    @staticmethod
    def get_fonts_statistics(path, exclude_unused_styles = False, exclude_comments = False):
        styles, events = AssParser.read_script(path)
        used_styles = defaultdict(UsageData)

        if exclude_unused_styles:
            used = set(event.style for event in events)
            for style in list(styles.keys()):
                if style not in used:
                    del styles[style]


        for name, info in styles.items():
            used_styles[info].styles.add(name)

        for event in events:
            if exclude_comments and event.is_comment:
                continue
            AssParser.process_event(event, used_styles, styles)
        return used_styles


    @staticmethod
    def process_event(event, used_styles, styles):
        blocks = AssParser.parse_tags(event.text)
        style = styles[event.style].clone()
        initial = style.clone()
        overriden = False
        for block in blocks:
            if isinstance(block, AssParser.AssBlockOverride):
                for tag in block.tags:
                    if tag.name == 'r':
                        style = styles[tag.get_value(event.style)].clone()
                        overriden = False
                    elif tag.name == 'b':
                        style = StyleInfo(style.fontname, bool(tag.get_value(initial.bold)), style.italic)
                        overriden = True
                    elif tag.name == 'i':
                        style = StyleInfo(style.fontname, style.bold, bool(tag.get_value(initial.italic)))
                        overriden = True
                    elif tag.name == 'fn':
                        style = StyleInfo(tag.get_value(initial.fontname), style.bold, style.italic)
                        overriden = True
            elif isinstance(block, AssParser.AssBlockPlain):
                used_style = used_styles[style]
                if not block.text:
                    continue
                if overriden:
                    used_style.lines.add(event.line_number)
                idx = 0
                while idx < len(block.text):
                    cur = block.text[idx]
                    if cur == '\\' and idx != (len(block.text) - 1):
                        idx += 1
                        next = block.text[idx]
                        if next == 'N' or next == 'n':
                            continue
                        if next == 'h':
                            cur = 0xA0 #I don't even
                        else:
                            idx -= 1
                    used_style.chars.add(cur)
                    idx += 1


    @staticmethod
    def parse_tags(text):
        if not text:
            return []

        blocks = []
        drawing = False
        cur = 0
        #todo: this whole thing is way too C++
        while cur < len(text):
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
        pos += 1
        work = text[pos:end]
        if work and work.find('\\') == -1:
            #comment line - do nothing
            pass
        else:
            block = AssParser.AssBlockOverride(work)
            blocks.append(block)
            for tag in block.tags:
                if tag.name == 'p':
                    if tag.value == '0':
                        drawing = False
                    else:
                        drawing = True
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
        with open(path, encoding='utf-8') as file:
            script = file.read()
        styles = {}
        events = []
        for line in script.splitlines():
            try:
                descriptor, value = line.split(':', 1)
            except ValueError:
                continue
            if descriptor not in {'Dialogue', 'Comment', 'Style'}:
                continue
            if descriptor in {'Dialogue', 'Comment'}:
                event = value.split(',', 9) #len(EventFormat) - 1
                ass_event = AssParser.AssEvent(len(events)+1, event[3], event[9].strip(), True if descriptor=='Comment' else False)
                events.append(ass_event)
            else:
                ass_style = value.split(',', 22) #len(AssParser.EventFormat) - 1
                style_info = StyleInfo.from_ass(ass_style[1], ass_style[7], ass_style[8])#
                styles[ass_style[0].strip()] = style_info
        return styles, events
