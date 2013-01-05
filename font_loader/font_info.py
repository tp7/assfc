from json import JSONEncoder
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

    class FontInfoJsonEncoder(JSONEncoder):
        def default(self, o):
            if isinstance(o, FontInfo):
                return {'path': o.path, 'names': o.names, 'full_names': o.full_names, 'styles': o.styles}
            else:
                return str(o)

    @staticmethod
    def deserialize(data):
        return FontInfo(data['names'], data['full_names'], data['styles'], data['path'], None)