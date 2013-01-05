from re import compile
from misc import cached_property


class AssParser(object):
    StyleFormat = ('Name', 'Fontname', 'Fontsize', 'PrimaryColour', 'SecondaryColour', 'OutlineColour',
                   'BackColour', 'Bold', 'Italic', 'Underline', 'StrikeOut', 'ScaleX', 'ScaleY', 'Spacing', 'Angle',
                   'BorderStyle', 'Outline', 'Shadow', 'Alignment', 'MarginL', 'MarginR', 'MarginV', 'Encoding')

    EventFormat = ('Layer', 'Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text')

    local_fonts_regex = compile(r"\\fn([^\\}]+)")

    def __init__(self, script_path):
        self.styles = []
        self.events = []
        self.__load_script(script_path)

    def __load_script(self, path):
        with open(path, encoding='utf-8') as file:
            script = file.read()
        for line in script.splitlines():
            try:
                descriptor, value = line.split(':', maxsplit=1)
            except:
                continue
            if descriptor not in {'Dialogue', 'Comment', 'Style'}:
                continue

            if descriptor in {'Dialogue', 'Comment'}:
                event = value.split(',', maxsplit=len(AssParser.EventFormat) - 1)
                event = {x: y.strip() for x, y in zip(AssParser.EventFormat, event)}
                event['Descriptor'] = descriptor
                event['LocalFonts'] = self.local_fonts_regex.findall(event['Text'])
                self.events.append(event)
            else:
                style = value.split(',', maxsplit=len(AssParser.StyleFormat) - 1)
                style = {x: y.strip() for x, y in zip(AssParser.StyleFormat, style)}
                self.styles.append(style)

    def font_used_in(self, font_name):
        styles = [x for x in self.styles if font_name == x['Fontname']]
        events = [x for x in self.events if font_name in x['LocalFonts']]
        return styles, events

    def get_fonts(self, exclude_unused_styles=False, exclude_comments=False):
        styles = (x for x in self.styles if x['Name'] in self.__used_styles_names) if exclude_unused_styles else self.styles
        events = (x for x in self.events if x['Descriptor'] == 'Dialogue') if exclude_comments else self.events
        return self.__get_fonts_used_in(styles, events)

    def __get_fonts_used_in(self, styles, events):
        fonts = set(x['Fontname'] for x in styles)
        for event in events:
            fonts.update(event['LocalFonts'])
        return list(fonts)

    @cached_property
    def __used_styles_names(self):
        return set((x['Style'] for x in self.events))
