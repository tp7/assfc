import os
import sys
from fnmatch import fnmatch
from json import JSONDecoder
import logging
from font_loader.font_info import FontInfo, FontStyle
from font_loader.ttf_parser import TTFFont
from font_loader.ttc_parser import TTCFont

APPNAME = "assfc"
WINDOWS_FONTS_FOLDER = os.environ['SYSTEMROOT'] + '\\Fonts'

SUPPORTED_FONTS_EXTENSIONS = {'.ttf', '.otf', '.ttc'}

is_supported_font = lambda x: os.path.splitext(x)[1] in SUPPORTED_FONTS_EXTENSIONS

def get_app_data_folder():
    if sys.platform == 'darwin':
        raise NotImplementedError("OSX support not implemented yet")
    elif sys.platform == 'win32':
        appdata = os.path.join(os.environ['APPDATA'], APPNAME)
    else:
        appdata = os.path.expanduser(os.path.join("~", "." + APPNAME))
    if not os.path.exists(appdata):
        os.mkdir(appdata)
    return appdata

def get_font_cache_file_path():
    return os.path.join(get_app_data_folder(), "font_cache.json")

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
        files = map(lambda x: os.path.join(path, x), filter(is_supported_font, os.listdir(path)))
        fonts = []
        for font_path in files:
            font = self.load_font(font_path)
            if isinstance(font,TTCFont):
                fonts.extend(font.get_infos())
            else:
                fonts.append(font.get_info())
        return fonts

    def load_font(self, path):
        if fnmatch(path, '*.ttc'):
            return TTCFont(path)
        else:
            return TTFFont(path)

    def __load_system_fonts(self):
        cache_file = get_font_cache_file_path()
        system_fonts_paths =  frozenset(map(lambda x: os.path.join(WINDOWS_FONTS_FOLDER, x), filter(is_supported_font, os.listdir(WINDOWS_FONTS_FOLDER))))

        loaded = []
        removed = []
        try:
            #let's try to load our cache
            with open(cache_file, 'r', encoding='utf-8') as file:
                cached_fonts = JSONDecoder(object_hook=FontInfo.deserialize).decode(file.read())

            #updating the cache - finding all removed/added files
            cached_paths = frozenset(map(lambda x: x.path, cached_fonts))
            removed = cached_paths.difference(system_fonts_paths)
            added = system_fonts_paths.difference(cached_paths)
            #loading all fonts except removed from cache
            loaded = list(filter(lambda x: x.path not in removed, cached_fonts))
        except:
            #we don't care what happened - just reindex everything
            added = system_fonts_paths

        for font_path in added:
            #indexing additional fonts
            font = self.load_font(font_path)
            if isinstance(font,TTCFont):
                loaded.extend(font.get_infos())
            else:
                loaded.append(font.get_info())

        if added or removed:
            # updating the cache
            with open(cache_file, 'w', encoding='utf-8') as file:
                file.write(FontInfo.FontInfoJsonEncoder(indent=4).encode(loaded))

        return loaded

    def discard_cache(self):
        cache = get_font_cache_file_path()
        if os.path.exists(cache):
            os.remove(cache)


    @property
    def fonts(self):
        return self.__fonts
