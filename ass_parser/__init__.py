import logging
from re import compile

class AssParser(object):
    global_fonts_regex = compile("Style:[^,\\n]+?,([^,]+)")
    local_fonts_regex = compile("Dialogue:.+?\\\\fn([^\\\\}]+)")

    def __init__(self, script_path):
        self.__load_script(script_path)

    def __load_script(self, path):
        with open(path, encoding='utf-8') as file:
            script = file.read()
        self.__parse_fonts(script)

    def __parse_fonts(self, script):
        global_fonts = self.global_fonts_regex.findall(script)
        local_fonts = self.local_fonts_regex.findall(script)
        global_fonts.extend(local_fonts)
        self.fonts = list(set(global_fonts))

    def get_fonts(self):
        return self.fonts
