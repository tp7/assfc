from misc import calculate_md5_for_file

class FontInfo(object):
    __slots__ = ['names', 'bold', 'italic', 'path', '__md5']

    def __init__(self, names, bold, italic, path, md5):
        self.names = names
        self.bold = bold
        self.italic = italic
        self.path = path
        self.__md5 = md5

    @property
    def md5(self):
        if not self.__md5:
            self.__md5 = calculate_md5_for_file(self.path)
        return self.__md5

