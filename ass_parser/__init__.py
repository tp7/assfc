from re import compile

class AssParser(object):
    StyleFormat = ('Name', 'Fontname', 'Fontsize', 'PrimaryColour', 'SecondaryColour', 'OutlineColour',
                   'BackColour', 'Bold', 'Italic', 'Underline', 'StrikeOut', 'ScaleX', 'ScaleY', 'Spacing', 'Angle',
                   'BorderStyle', 'Outline', 'Shadow', 'Alignment', 'MarginL', 'MarginR', 'MarginV', 'Encoding')

    EventFormat = ('Layer', 'Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text')

    local_fonts_regex = compile(r"\\fn([^\\}]+)")

    def __init__(self, script_path):
        self.styles = dict()
        self.events = []
        self.fonts = []
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
                event = value.split(',', maxsplit=len(AssParser.EventFormat)-1)
                event = {x:y.strip() for x,y in zip(AssParser.EventFormat, event)}
                self.events.append(event)
            else:
                style = value.split(',', maxsplit=len(AssParser.StyleFormat)-1)
                style = {x:y.strip() for x, y in zip(AssParser.StyleFormat, style)}
                self.styles[style['Name']] = style

        self.__parse_fonts()

    def __parse_fonts(self):
        fonts = [x['Fontname'] for x in self.styles.values()]
        for event in self.events:
            local_fonts = self.local_fonts_regex.findall(event['Text'])
            fonts.extend(local_fonts)
        self.fonts = list(set(fonts))

