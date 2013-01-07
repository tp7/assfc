from misc import calculate_md5_for_file

class FontStyle:
    Regular = 1
    Bold = 2
    Italic = 3
    BoldItalic = 4

    names = ['Undefined', 'Regular', 'Bold', 'Italic', 'Bold Italic']

    @staticmethod
    def get_style(original, new):
        if original is FontStyle.Bold and new is FontStyle.Italic \
        or original is FontStyle.Italic and new is FontStyle.Bold:
            return FontStyle.BoldItalic
        else:
            return new

    @staticmethod
    def to_string(style):
        return FontStyle.names[style]

    @staticmethod
    def create(bold, italic):
        if bold and italic:
            return FontStyle.BoldItalic
        if bold:
            return FontStyle.Bold
        if italic:
            return FontStyle.Italic
        return FontStyle.Regular



class FontInfo(object):
    __slots__ = ['names', 'style', 'path', '__md5']

    def __init__(self, names, style, path, md5):
        self.names = names
        self.style = style
        self.path = path
        self.__md5 = md5

    @property
    def md5(self):
        if not self.__md5:
            self.__md5 = calculate_md5_for_file(self.path)
        return self.__md5

