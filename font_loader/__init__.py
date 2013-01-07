import os
from fnmatch import fnmatch
import logging
import sys
import pickle
from font_loader.font_info import FontInfo
from font_loader.ttf_parser import TTFFont
from font_loader.ttc_parser import TTCFont
from misc import SYSTEM_FONTS_FOLDERS, get_app_data_folder, enumerate_files_in_directory


is_supported_font = lambda x: os.path.splitext(x)[1].lower() in {'.ttf', '.otf', '.ttc'}

class FontLoader(object):
    def __init__(self, font_dirs = None, load_system_fonts = True):
        font_files = set()

        if load_system_fonts:
            font_files.update(self.__enumerate_system_fonts())

        if font_dirs:
            for dir in font_dirs:
                font_files.update(self.__enumerate_font_files(dir))

        self.__load_fonts(font_files)

    def get_fonts_for_list(self, font_list):
        found = []
        not_found = []
        for font_info in font_list.keys():
            logging.debug('Processing font %s...' % font_info)
            candidates = []
            best_candidate = None
            for font in self.fonts:
                for name in font.names:
                    if name.lower() == font_info.fontname.lower():
                        candidates.append(font)
                        break

            logging.debug('Found %i candidates' % len(candidates))

            if not candidates:
                not_found.append(font_info)
                continue

            for candidate in candidates:
                if candidate.bold == font_info.bold and candidate.italic == font_info.italic:
                    best_candidate = candidate
                    logging.debug("Found exact match")
                    break

            if not best_candidate:
                logging.debug('Failed to find exact match. Looking for regular version...')
                for candidate in candidates:
                    if candidate.bold == False and candidate.italic == False:
                        best_candidate = candidate
                        logging.debug('Found regular one')
                        break

            if not best_candidate:
                not_found.append(font_info)
                continue

            if best_candidate in found:
                logging.debug("Font %s already exists" % best_candidate.names[0])
                continue

            for already_added in found:
                if already_added.md5 == best_candidate.md5:
                    logging.info("Duplicate font found. Skipping.")
                    continue

            found.append(best_candidate)
            logging.debug('Found font %s at %s' % (font_info, best_candidate.path))
        return found, not_found

    @staticmethod
    def __enumerate_font_files(directory):
        files =  enumerate_files_in_directory(directory)
        return [x['path'] for x in files if is_supported_font(x['path'])]

    @staticmethod
    def __enumerate_system_fonts():
        system_fonts_paths = []
        for f in SYSTEM_FONTS_FOLDERS:
            system_fonts_paths.extend(FontLoader.__enumerate_font_files(f))
        #todo: additional fonts from registry
        return system_fonts_paths

    def __load_fonts(self, fonts_paths):
        cache_file = FontLoader.get_font_cache_file_path()
        removed = []
        self.fonts = []
        try:
            #let's try to load our cache
            with open(cache_file, 'rb') as file:
                cached_fonts = pickle.load(file)
                #updating the cache - finding all removed/added files
            cached_paths = frozenset(map(lambda x: x.path, cached_fonts))
            removed = cached_paths.difference(fonts_paths)
            added = fonts_paths.difference(cached_paths)
            self.fonts = list(filter(lambda x: x.path not in removed, cached_fonts))
        except:
            print(sys.exc_info())
            #we don't care what happened - just reindex everything
            added = fonts_paths

        for font_path in added:
            if fnmatch(font_path, '*.ttc'):
                self.fonts.extend(TTCFont(font_path).get_infos())
            else:
                self.fonts.append(TTFFont(font_path).get_info())

        if added or removed:
            # updating the cache
            with open(cache_file, 'wb') as file:
                pickle.dump(self.fonts, file, -1)

    @staticmethod
    def discard_cache():
        cache = FontLoader.get_font_cache_file_path()
        if os.path.exists(cache):
            os.remove(cache)

    @staticmethod
    def get_font_cache_file_path():
        return os.path.join(get_app_data_folder(), "font_cache.bin")

