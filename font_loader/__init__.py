from os import listdir
import os
import hashlib
from fnmatch import fnmatch
import logging
import winreg
from re import compile
from font_loader.ttf_parser import TTFFont
from font_loader.ttc_parser import TTCFont

def calculate_md5_for_file(path, block_size=2**20):
    md5 = hashlib.md5()
    with open(path, 'rb') as file:
        while True:
            data = file.read(block_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

class FontInfo(object):
    __slots__ = ['names', 'full_names', 'path', '__md5']

    def __init__(self, names, full_names, path, md5):
        self.names = names
        self.full_names = full_names
        self.path = path
        self.__md5 = md5

    def md5(self):
        if not self.__md5:
            self.__md5 = calculate_md5_for_file(self.path)
        return self.__md5


class FontLoader(object):
    def __init__(self, font_dirs = None, load_system_fonts = True):
        self.__fonts = []
        #loading windows fonts
        if load_system_fonts:
            self.__fonts.extend(self.__load_system_fonts())
        #loading fonts from all specified folders
        if font_dirs:
            for dir in font_dirs:
                self.__fonts.extend(self.load_fonts_in_directory(dir))

    def get_fonts_for_list(self, font_names):
        found = []
        not_found = []
        for font_name in font_names:
            found_font = None
            for font in self.__fonts:
                for name in (font.names + font.full_names):
                    if name.lower() == font_name.lower():
                        found_font = font
                        break

            if not found_font:
                not_found.append(font_name)
                logging.debug("Font not found: %s" % font_name)
                continue

            if found_font in found:
                logging.debug("Font %s already exists" % found_font.name)
                continue

            for already_added in found:
                if already_added.md5 == found_font.md5:
                    logging.debug("Duplicate font found. Skipping.")
                    continue

            found.append(found_font)
            logging.debug('Font found: %s. File: %s' % (font_name, found_font.path))

        return found, not_found


    def load_fonts_in_directory(self, path):
        files = filter(lambda x: fnmatch(x, '*.ttf') or fnmatch(x, '*.otf') or fnmatch(x, '*.ttc'), listdir(path) )
        fonts = []
        for file_name in files:
            file_path = os.path.join(path, file_name)
            font_file = TTCFont(file_path) if fnmatch(file_path, '*.ttc') else TTFFont(file_path)
            fonts.append(FontInfo(font_file.get_names(), font_file.get_full_names(), file_path, None))
        return fonts

    def __load_system_fonts(self):
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts\\") as key:
            system_fonts = []
            info = winreg.QueryInfoKey(key)
            for index in range(info[1]):
                value = winreg.EnumValue(key, index)
                path = value[1] if os.path.isabs(value[1]) else "%SystemRoot%\\Fonts\\" + value[1]
                font_name_regex = compile(r'\s\(.*\)$')
                font_name = font_name_regex.sub('',value[0])
                font_info = FontInfo([font_name], [font_name], path, None)
                system_fonts.append(font_info)
            return system_fonts



