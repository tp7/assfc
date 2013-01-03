import hashlib
import logging

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
    __slots__ = ['names', 'full_names', 'styles', 'path', '__md5']

    class FontStyle:
        Regular = 0
        Bold = 1
        Italic = 2

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
