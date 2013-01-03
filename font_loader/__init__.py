from os import listdir
import os
from fnmatch import fnmatch
import logging
import winreg
from font_loader.font_info import FontInfo
from font_loader.ttf_parser import TTFFont
from font_loader.ttc_parser import TTCFont

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
                    if name.lower().find(font_name.lower()) != -1:
                        found_font = font
                        break

            if not found_font:
                not_found.append(font_name)
                logging.warning("Font not found: %s" % font_name)
                continue

            if found_font in found:
                logging.debug("Font %s already exists" % found_font.names[0])
                continue

            for already_added in found:
                if already_added.md5 == found_font.md5:
                    logging.info("Duplicate font found. Skipping.")
                    continue

            found.append(found_font)
            logging.debug('Font found: %s. File: %s' % (font_name, found_font.path))

        return found, not_found


    def load_fonts_in_directory(self, path):
        files = filter(lambda x: fnmatch(x, '*.ttf') or fnmatch(x, '*.otf') or fnmatch(x, '*.ttc'), listdir(path) )
        fonts = []
        for file_name in files:
            file_path = os.path.join(path, file_name)
            if fnmatch(file_path, '*.ttc'):
                font_file = TTCFont(file_path)
                fonts.extend(font_file.get_info())
            else:
                font_file = TTFFont(file_path)
                fonts.append(font_file.get_info())
        return fonts

    def __load_system_fonts(self):
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts\\") as key:
            system_fonts = []
            info = winreg.QueryInfoKey(key)
            for index in range(info[1]):
                value = winreg.EnumValue(key, index)
                path = value[1] if os.path.isabs(value[1]) else "C:\\Windows\\Fonts\\" + value[1]
                font_info = FontInfo((value[0],), (value[0],), None, path, None)
                system_fonts.append(font_info)
            return system_fonts

    @property
    def fonts(self):
        return self.__fonts
