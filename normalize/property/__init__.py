
from __future__ import absolute_import

import weakref

from normalize.property.meta import MetaProperty


class Property(property):
    __metaclass__ = MetaProperty

    def __init__(self, ro=False, default=None, required=False,
                 fget=None, fset=None, fdel=None, doc=None,
                 traits=None):
        super(Property, self).__init__(fget, fset, fdel, doc)
        self.ro = ro
        self.default = default
        self.required = required
        self.name = None
        self.class_ = None

    @property
    def bound(self):
        return bool(self.class_)

    def bind(self, class_, name):
        self.name = name
        self.class_ = weakref.ref(class_)

    def init_prop(self, obj, value):
        obj.__dict__[self.name] = value

    def __get__(self, obj, type_=None):
        """Default getter; does NOT fall back to regular descriptor behavior
        """
        if self.name not in obj.__dict__:
            raise AttributeError
        return obj.__dict__[self.name]


class LazyProperty(Property):
    __trait__ = "lazy"

    def __init__(self, lazy=True, **kwargs):
        self.lazy = True
        super(LazyProperty, self).__init__(**kwargs)

    def __get__(self, obj, type_=None):
        if callable(self.default):
            rv = self.default()
        else:
            rv = self.default
        obj.__dict__[self.name] = rv
        return rv


class RWProperty(Property):
    __trait__ = "rw"

    def __get__(self, obj, type_=None):
        return obj.__dict__[self.name]

    def __set__(self, obj, value):
        obj.__dict__[self.name] = value

    def __delete__(self, instance):
        """
        Note: instance is normally an instance of a Record
        """
        if self.required:
            raise ValueError("%s is required" % self.name)
        super(RWProperty, self).__delete__(instance)


class CheckedProperty(Property):
    __trait__ = "check"

    def __init__(self, check=None, **kwargs):
        if not callable(check):
            raise Exception("'check' is required and must be callable")
        self.check = check
        super(CheckedProperty, self).__init__(**kwargs)


class CheckedRWProperty(RWProperty, CheckedProperty):
    def __set__(self, obj, value):
        if not self.check(obj):
            raise ValueError(
                "field %s may not have value %r" % (self.name, value)
            )
        super(CheckedRWProperty, self).__set__(obj, value)
