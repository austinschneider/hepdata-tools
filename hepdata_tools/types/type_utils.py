import typing


def named_tuple_to_py(self):
    """Convert named tuples to a primative type representation"""
    d = self._asdict()
    to_del = []
    for k, v in d.items():
        if hasattr(v, "to_py"):
            d[k] = v.to_py()
        elif isinstance(v, str):
            pass
        elif hasattr(v, "__iter__"):
            d[k] = [x.to_py() if hasattr(x, "to_py") else x for x in v]
        elif v is None:
            to_del.append(k)
    for k in to_del:
        del d[k]
    return d


def get_type_class(typ):
    """Get the base class of objects from the typing library"""
    try:
        # Python 3.5 / 3.6
        return typ.__extra__
    except AttributeError:
        try:
            # Python 3.7
            return typ.__origin__
        except AttributeError:
            return typ


def check_instance(obj, typ):
    """Check if an object is an instance of the described type
    Accounts for the use of typing.List and typing.Union"""
    base_type = get_type_class(typ)
    if base_type is typing.Union:
        if typ != typing.Union.__getitem__(typ.__args__):
            raise RuntimeError("typing.Union does not match itself!")
        types = typ.__args__
        for t in types:
            if check_instance(obj, t):
                return True
        return False
    elif base_type is dict:
        if not isinstance(obj, base_type):
            return False
        if hasattr(typ, "__args__"):
            if typ is typing.Dict[typ.__args__[0], typ.__args__[1]]:
                k_type, v_type = typ.__args__
                for k, v in obj.items():
                    if not check_instance(k, k_type):
                        return False
                    if not check_instance(v, v_type):
                        return False
                return True
            else:
                raise RuntimeError("typing.Dict does not match itself!")
        else:
            return True
    elif base_type is list:
        if not isinstance(obj, base_type):
            return False
        if hasattr(typ, "__args__"):
            if typ is typing.List[typ.__args__[0]]:
                v_type = typ.__args__[0]
                for v in obj:
                    if not check_instance(v, v_type):
                        return False
                return True
            else:
                raise RuntimeError("typing.List does not match itself!")
        else:
            return True
    else:
        return isinstance(obj, base_type)


def check_tuple_type(self):
    """Check that a named tuple is initialized with the correct types"""
    for field, field_type in self._field_types.items():
        obj = getattr(self, field)
        if not check_instance(obj, field_type):
            raise TypeError("{} must be {}".format(field, (field_type)))
    return self


class NamedTupleMeta(typing.NamedTupleMeta):
    """A fix for multiple inheritance with typing.NamedTuple"""

    def __new__(cls, typename, bases, ns):
        cls_obj = super().__new__(cls, typename + "_nm_base", bases, ns)
        bases = bases + (cls_obj,)
        return type(typename, bases, {})


class TypeCheck:
    """Inheritable type checking and conversions for NamedTuples"""

    def __init__(self, *args, **kwargs):
        self.check_type()

    def to_py(self):
        return named_tuple_to_py(self)

    def check_type(self):
        return check_tuple_type(self)
