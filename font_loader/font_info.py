import logging
from misc import calculate_md5_for_file, flag_enum

FontStyle = flag_enum('FontStyle', 'Regular','Bold','Italic')

class FontInfo(object):
    __slots__ = ['names', 'full_names', 'styles', 'path', '__md5']

    def __init__(self, names, full_names, styles, path, md5):
        self.names = names
        self.full_names = full_names
        self.styles = styles
        self.path = path
        self.__md5 = md5

    @property
    def md5(self):
        if not self.__md5:
            self.__md5 = calculate_md5_for_file(self.path)
        return self.__md5

