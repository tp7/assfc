import hashlib
import logging
import os
import sys
from re import compile

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
    logging.debug('Enumerating files in directory %s' % directory)
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


APPNAME = "assfc"

def get_app_data_folder():
    if sys.platform == 'win32':
        appdata = os.path.join(os.environ['APPDATA'], APPNAME)
    elif sys.platform == 'darwin':
        from AppKit import NSSearchPathForDirectoriesInDomains
        # http://developer.apple.com/DOCUMENTATION/Cocoa/Reference/Foundation/Miscellaneous/Foundation_Functions/Reference/reference.html#//apple_ref/c/func/NSSearchPathForDirectoriesInDomains
        # NSApplicationSupportDirectory = 14
        # NSUserDomainMask = 1
        # True for expanding the tilde into a fully qualified path
        appdata = os.path.join(NSSearchPathForDirectoriesInDomains(14, 1, True)[0], APPNAME)
    else:
        appdata = os.path.expanduser(os.path.join("~", "." + APPNAME))

    if not os.path.exists(appdata):
        os.mkdir(appdata)
    return appdata