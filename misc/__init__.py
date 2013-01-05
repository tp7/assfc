import hashlib
import os
import sys


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


def flag_enum(name, *names):
    #extend frozenset with has_flag method
    class EnumElement(frozenset):
        def has_flag(self,flag):
            return self.issuperset(flag)

        def __repr__(self):
            return ', '.join(self)

        #make all intersection/union/whatever operations
        #return an EnumElement instead of a frozenset
        @classmethod
        def _wrap_methods(cls,names):
            def wrap_method(name):
                def inner(self, *args):
                    result = getattr(super(cls, self), name)(*args)
                    return EnumElement(result)
                inner.fn_name = name
                setattr(cls, name, inner)
            for name in names:
                wrap_method(name)
    EnumElement._wrap_methods(['__ror__', '__or__', '__sub__', '__rsub__',
                               '__and__', '__rand__', '__rxor__', '__xor__',
                               'intersection', 'difference', 'union',
                               'symmetric_difference','copy'
    ])

    #define a base class for enumeration
    class EnumBase:
        @classmethod
        def is_defined(cls,attr):
            return attr in cls.__dict__

    #and then add EnumElements to it
    attrs = {}
    for n in names:
        attrs[n] = EnumElement([n])
    return type(name, (EnumBase,), attrs)


APPNAME = "assfc"
WINDOWS_FONTS_FOLDER = os.environ['SYSTEMROOT'] + '\\Fonts'

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