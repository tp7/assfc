from re import compile
import sys
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
                descriptor, value = line.split(':', 1)
            except:
                continue
            if descriptor not in {'Dialogue', 'Comment', 'Style'}:
                continue

            if descriptor in {'Dialogue', 'Comment'}:
                event = value.split(',', len(AssParser.EventFormat) - 1)
                event = {x: y.strip() for x, y in zip(AssParser.EventFormat, event)}
                event['Descriptor'] = descriptor
                event['LocalFonts'] = self.local_fonts_regex.findall(event['Text'])
                event['LineNumber'] = len(self.events)
                self.events.append(event)
            else:
                style = value.split(',', len(AssParser.StyleFormat) - 1)
                style = {x: y.strip() for x, y in zip(AssParser.StyleFormat, style)}
                self.styles.append(style)

    def get_lines_font_used_in(self, font_name, exclude_unused_styles=False, exclude_comments=False):
        events, styles = self.__filter_events_and_styles(exclude_unused_styles, exclude_comments)
        styles = (style for style in styles if font_name == style['Fontname'])

        lines = set(event['LineNumber'] for event in events if font_name in event['LocalFonts'])
        for s in styles:
            lines.update(self.get_lines_style_used_in(s['Name'],exclude_comments))
        return list(lines)

    def get_lines_style_used_in(self, style_name, exclude_comments=False):
        events = self.__only_dialogue_events if exclude_comments else self.events
        return [event['LineNumber'] for event in events if style_name == event['Style']]

    def get_fonts(self, exclude_unused_styles=False, exclude_comments=False):
        events, styles = self.__filter_events_and_styles(exclude_unused_styles, exclude_comments)
        fonts = set(style['Fontname'] for style in styles)
        fonts.update(font for event in events for font in event['LocalFonts'])
        return list(fonts)

    def __filter_events_and_styles(self, exclude_unused_styles=False, exclude_comments=False ):
        styles = self.__used_styles if exclude_unused_styles else self.styles
        events = self.__only_dialogue_events if exclude_comments else self.events
        return events, styles

    @cached_property
    def __used_styles(self):
        return [style for style in self.styles if style['Name'] in set((event['Style'] for event in self.events))]

    @cached_property
    def __only_dialogue_events(self):
        return [event for event in self.events if event['Descriptor'] == 'Dialogue']
