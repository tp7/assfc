import hashlib
import logging
import os
import sys
from re import compile


class cached_property(object):
    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, None)
        if value is None:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value

def calculate_md5_for_file(path, block_size=2**20):
    md5 = hashlib.md5()
    with open(path, 'rb') as file:
        while True:
            data = file.read(block_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

def enumerate_files_in_directory(directory):
    files = []
    if sys.platform == 'win32':
        windows_enumerate_directory(directory, files)
    else:
        linux_enumerate_directory(directory, files)
    return files

def linux_enumerate_directory(directory, files_collection):
    for path, subdirs, files in os.walk(directory):
        for name in files:
            files_collection.append(os.path.join(path, name))

def windows_enumerate_directory(directory, files):
    from ctypes import windll, wintypes, byref
    FILE_ATTRIBUTE_DIRECTORY = 0x10
    INVALID_HANDLE_VALUE = -1
    BAN = ('.', '..')

    FindFirstFile = windll.kernel32.FindFirstFileW
    FindNextFile  = windll.kernel32.FindNextFileW
    FindClose     = windll.kernel32.FindClose

    out  = wintypes.WIN32_FIND_DATAW()
    fldr = FindFirstFile(os.path.join(directory, "*"), byref(out))

    if fldr == INVALID_HANDLE_VALUE:
        raise ValueError("invalid handle!")
    try:
        while True:
            if out.cFileName not in BAN:
                isdir = out.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY

                if isdir:
                    windows_enumerate_directory(os.path.join(directory, out.cFileName), files)
                else:
                    files.append(os.path.join(directory, out.cFileName))
            if not FindNextFile(fldr, byref(out)):
                break
    finally:
        FindClose(fldr)

def read_linux_font_dirs():
    linux_font_dir = compile(r"<dir>(.+?)</dir>")
    with open('/etc/fonts/fonts.conf') as file:
        return linux_font_dir.findall(file.read())

APPNAME = "assfc"

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