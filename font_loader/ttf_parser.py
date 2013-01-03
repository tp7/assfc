from collections import namedtuple
import logging
import struct

OffsetTable = namedtuple('OffsetTable', ['version', 'num_tables', 'search_range', 'entry_selector', 'range_shift'])
TableDirectory = namedtuple('TableDirectory', ['tag', 'check_sum', 'offset', 'length'])
NamingTable = namedtuple('NamingTable', ['format_selector', 'number_of_name_records', 'offset_start_of_string_storage'])
NameRecord = namedtuple('NameRecord', ['platform_id', 'encoding_id', 'language_id', 'name_id', 'string_length', 'offset_from_storage_area'])


class TTFFont(object):
    platform_id_2_encodings = {
        0:'ascii',
        1:'ISO-10646',
        2:'ISO-8859-1'
    }

    class TTFNameId:
        CopyrightNotice = 0
        FontFamilyName = 1
        FontSubFamilyName = 2
        UniqueIdentifier = 3
        FullFontName = 4
        Version = 5
        PostScriptName = 6,
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
        self.headers = {}
        self.__bold = False
        self.__regular = False
        self.__italic = False
        self.__names = set()
        self.__full_names = set()
        self.parse(path, offset)

    def parse(self, path, offset):
        with open(path,'rb') as file:
            file.seek(offset)
            data =  struct.unpack('>IHHHH', file.read(12))
            offset_table = OffsetTable(data[0], data[1], data[2], data[3], data[4])

            for i in range(offset_table.num_tables):
                data = struct.unpack('>4sLLL', file.read(16))
                table_directory = TableDirectory(data[0].decode('utf-8'), data[1], data[2], data[3])

                if table_directory.tag != 'name':
                    continue

                file.seek(table_directory.offset)
                data =  struct.unpack('>HHH', file.read(6))
                naming_table = NamingTable(data[0], data[1], data[2])

                names = []
                for record in range(naming_table.number_of_name_records):
                    data = struct.unpack('>HHHHHH', file.read(12))
                    names.append(NameRecord(data[0], data[1], data[2], data[3], data[4], data[5]))

                for name in names:
                    file.seek(table_directory.offset + naming_table.offset_start_of_string_storage + name.offset_from_storage_area)
                    size = int(name.string_length)
                    if name.platform_id == 0 or name.platform_id == 3:
                        value = struct.unpack('>' + str(size)+'s', file.read(size))[0].decode('utf-16be')

                    elif name.platform_id == 2:
                        value = struct.unpack('>' + str(size)+'s', file.read(size))[0].decode(self.platform_id_2_encodings[name.encoding_id])

                    elif name.platform_id == 1:
                        #this is probably 'a bit' broken
                        value = struct.unpack('>' + str(size)+'s', file.read(size))[0].decode('ISO 8859-1')
                    else:
                        logging.debug("Error while parsing font file %s. Name data: %s" % (path, str(name)))
                        value = ''
                    self.__set_name_by_id(name.name_id, value)
                return

    def __set_name_by_id(self, id, value):
        if id is self.TTFNameId.FontFamilyName:
            self.__names.add(value)
        elif id is self.TTFNameId.FullFontName:
            self.__full_names.add(value)
        elif id is self.TTFNameId.FontSubFamilyName:
            self.__parse_styles(value)

        if id not in self.headers:
            self.headers[id] = []
        self.headers[id].append(value)

    def __parse_styles(self, sub_family_name):
        name = sub_family_name.lower()
        if name.find('bold') is not -1:
            self.__bold = True
        if name.find('italic') is not -1:
            self.__italic = True
        if name.find('regular') is not -1 or name.find('normal') is not -1 or name.find('standard') is not -1:
            self.__regular = True

    def get_names(self):
        return list(self.__names)

    def get_full_names(self):
        return list(self.__names)

    def is_bold(self):
        return self.__bold

    def is_regular(self):
        return self.__regular

    def is_italic(self):
        return self.__italic

