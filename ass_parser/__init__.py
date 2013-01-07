from collections import namedtuple, defaultdict
import logging
from re import compile

class StyleInfo(object):
    __slots__ = ['fontname', 'bold', 'italic']

    def __init__(self, fontname, bold, italic):
        self.fontname = fontname
        self.bold = bold
        self.italic = italic

    def __repr__(self):
        return '%s (Bold: %s, Italic: %s)' % (self.fontname, str(self.bold), str(self.italic))

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def clone(self):
        return StyleInfo(self.fontname, self.bold, self.italic)

    @staticmethod
    def from_ass(fontname, bold, italic):
        return StyleInfo(fontname, bold == '-1', italic == '-1')

class UsageData(object):
    #styles refer to ASS styles defined globally
    __slots__ = ['lines', 'styles', 'has_chars']

    def __init__(self):
        self.lines = set()
        self.styles = set()
        self.has_chars = False

    def __repr__(self):
        lines = list(self.lines)
        lines.sort()
        return 'Styles: %s, lines: %s' % (self.styles, lines)


class AssParser(object):
    AssEvent = namedtuple('AssEvent', ['line_number', 'style', 'text', 'is_comment'] )

    AssBlockUseless = namedtuple('Useless', ['text'])
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
        tag_regex = compile(r'\\(i(?=[\d\\])|i(?=$)|b(?=[\d\\])|b(?=$)|fn)((?<=fn)[^\\]*|\d*)')

        def __init__(self, text):
            self.tags = [AssParser.AssTag(f[0], f[1]) for f in self.tag_regex.findall(text)]

        def __repr__(self):
            return 'OverrideBlock(text=%s)' %  ''.join(('\\%s%s' %(tag.name, tag.value) for tag in self.tags))

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
#        for key, value in used_styles.items():
#            print('%s: %s' %(str(key).ljust(55), value ))
        return used_styles

    @staticmethod
    def process_event(event, used_styles, styles):
        blocks = AssParser.parse_tags(event.text)
        style = styles[event.style].clone()
        initial = style
        overriden = False
        for block in blocks:
            if isinstance(block, AssParser.AssBlockOverride):
                for tag in block.tags:
#                    print(tag.name)
                    if tag.name == 'r':
                        style = styles[tag.get_value(event.style)].clone()
                        overriden = False
                    elif tag.name == 'b':
                        style.bold = bool(tag.get_value(initial.bold))
                        overriden = True
                    elif tag.name == 'i':
                        style.italic = bool(tag.get_value(initial.italic))
                        overriden = True
                    elif tag.name == 'fn':
                        style.fontname = tag.get_value(initial.fontname)
                        overriden = True
            elif isinstance(block, AssParser.AssBlockPlain):
                if not block.text:
                    continue
                if overriden:
                    used_styles[style].lines.add(event.line_number)
                used_styles[style].has_chars = True
            #do nothing with AssBlockUseless



    @staticmethod
    def parse_tags(text):
        if not text:
            return AssParser.AssBlockUseless(''), #this is a tuple. Yeah, I love Python cuz it's so obvious. Wait, you didn't notice that comma?

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
            #comment line
            blocks.append(AssParser.AssBlockUseless(work))
        else:
            block = AssParser.AssBlockOverride(work)
            blocks.append(block)
            for tag in block.tags:
                if tag.name == 'p':
                    if tag.value == '0':
                        drawing = True
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
            blocks.append(AssParser.AssBlockUseless(work))
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
            except:
                continue
            if descriptor not in {'Dialogue', 'Comment', 'Style'}:
                continue
            if descriptor in {'Dialogue', 'Comment'}:
                event = value.split(',', 9) #len(EventFormat) - 1
                ass_event = AssParser.AssEvent(len(events)+1, event[3], event[9].strip(), True if descriptor=='Comment' else False)
                events.append(ass_event)
            else:
                ass_style = value.split(',', 22) #len(AssParser.EventFormat) - 1
                style_info = StyleInfo.from_ass(ass_style[1], ass_style[7], ass_style[8])# AssParser.AssStyle(style[0].strip(), style[1], style[7], style[8])
                styles[ass_style[0].strip()] = style_info
        return styles, events
