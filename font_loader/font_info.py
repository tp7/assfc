from misc import calculate_md5_for_file

class FontInfo(object):
    __slots__ = ['names', 'bold', 'italic', 'weight', 'path', '__md5']

    def __init__(self, names, bold, italic, weight, path, md5):
        self.names = names
        self.bold = bold
        self.italic = italic
        self.weight = weight
        self.path = path
        self.__md5 = md5

    @property
    def md5(self):
        if not self.__md5:
            self.__md5 = calculate_md5_for_file(self.path)
        return self.__md5

class FontWeight(object):
    FW_THIN = 100
    FW_EXTRALIGHT = 200
    FW_LIGHT = 300
    FW_NORMAL = 400
    FW_MEDIUM = 500
    FW_SEMIBOLD = 600
    FW_BOLD = 700
    FW_EXTRABOLD = 800
    FW_BLACK = 900

