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

FontStyle = flag_enum('FontStyle', 'Undefined','Regular','Bold','Italic')

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
