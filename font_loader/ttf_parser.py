from collections import namedtuple, defaultdict
import logging
import struct
from font_loader.font_info import FontInfo

OffsetTable = namedtuple('OffsetTable', ['version', 'num_tables', 'search_range', 'entry_selector', 'range_shift'])
TableDirectory = namedtuple('TableDirectory', ['tag', 'check_sum', 'offset', 'length'])
NamingTable = namedtuple('NamingTable', ['format_selector', 'number_of_name_records', 'offset_start_of_string_storage'])
NameRecord = namedtuple('NameRecord', ['platform_id', 'encoding_id', 'language_id', 'name_id', 'string_length', 'offset_from_storage_area'])


class TTFFont(object):
    platform_id_3_encodings = {
        0:'ISO-8859-1',
        1:'utf-16be',
        2:'utf-16be',
        3:'gb2312',
        4:'big5',
        6:'johab',
        10:'utf-16be'
    }

    class TTFNameId:
        CopyrightNotice = 0
        FontFamilyName = 1
        FontSubFamilyName = 2
        UniqueIdentifier = 3
        FullFontName = 4
        Version = 5
        PostScriptName = 6
        Trademark = 7
        ManufacturerName = 8
        Designer = 9
        Description = 10
        URLVendor = 11
        URLDesigner = 12
        LicenseDescription = 13
        LicenseInfoURL = 14
        Reserved = 15
        PreferredFamily = 16
        PreferredSubfamily = 17
        CompatibleFull_MacintoshOnly = 18
        SampleText = 19
        PostScriptCIDFindFontName = 20
        WWSFamilyName = 21
        WWSSubfamilyName = 22

    def __init__(self, path, offset=0):
        self.headers = defaultdict(list)
        self.__bold = False
        self.__italic = False
        self.__names = set()
        self.__path = path
        self.parse(self.__path, offset)

    def parse(self, path, offset):
        with open(path,'rb') as file:
            file.seek(offset)
            data =  struct.unpack('>IHHHH', file.read(12))
            offset_table = OffsetTable._make(data)

            for i in range(offset_table.num_tables):
                data = struct.unpack('>4sLLL', file.read(16))
                table_directory = TableDirectory(data[0].decode('utf-8'), data[1], data[2], data[3])

                if table_directory.tag != 'name':
                    continue

                file.seek(table_directory.offset)
                data =  struct.unpack('>HHH', file.read(6))
                naming_table = NamingTable._make(data)

                names = []
                for record in range(naming_table.number_of_name_records):
                    data = struct.unpack('>HHHHHH', file.read(12))
                    names.append(NameRecord._make(data))

                for name in names:
                    file.seek(table_directory.offset + naming_table.offset_start_of_string_storage + name.offset_from_storage_area)
                    size = int(name.string_length)
                    string = file.read(size)
                    if name.platform_id == 3:
                        value = self.__decode_string(string,self.platform_id_3_encodings[name.encoding_id])

                    elif name.platform_id == 2:
                        value = self.__decode_string(string,'ISO 8859-1')

                    elif name.platform_id == 1:
                        #this is probably 'a bit' broken
                        value = self.__decode_string(string,'ISO 8859-1')
                    elif name.platform_id == 0:
                        try:
                            value = self.__decode_string(string,'utf-16be')
                        except UnicodeDecodeError:
                            logging.debug("Couldn't decode a string with PlatformID = 0 as UTF-16, trying UTF-8. Font file: %s. Name data: %s" % (path, str(name)))
                            value = self.__decode_string(string,'utf-8')
                    else:
                        logging.error("Unknown Platform Id in font file %s. Name data: %s" % (path, str(name)))
                        continue
                    self.__set_name_by_id(name.name_id, value)
                return

    def __decode_string(self,bytes,encoding):
        return struct.unpack('>' + str(len(bytes))+'s', bytes)[0].decode(encoding)

    def __set_name_by_id(self, id, value):
        if id is self.TTFNameId.FontFamilyName or id is self.TTFNameId.FullFontName:
            self.__names.add(value)
        elif id is self.TTFNameId.FontSubFamilyName:
            self.__parse_styles(value)

        self.headers[id].append(value)

    def __parse_styles(self, sub_family_name):
        name = sub_family_name.lower()
        if name.find('bold') is not -1:
            self.__bold = True
        if name.find('italic') is not -1:
            self.__italic = True

    def print_headers(self):
        types = {value:key for key, value in self.TTFNameId.__dict__.items()}
        for id, value in self.headers.items():
            print(str(types[id]).ljust(25), value)

    def get_info(self):
        return FontInfo(list(self.__names), self.__bold, self.__italic, self.__path, None)

