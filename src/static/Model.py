#!/usr/bin/env python3
#! -*- coding=utf-8 -*-

class Model(dict, metaclass=MdoelMetaclass):
    #构造方法
    def __init__(self, **kw):
        super(Model,self).__init__(**kw)
    #统一的得到属性方法
    #只有在没有找到属性的情况下才会调用getattr
    def __getattr__(self, key):
        try:
            return self[key]
        except keyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)
    
    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key)

    def getValueOrDefault(self, key):
        value = getattr(self, key)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s:%s' % (key, str(value)))
                setattr(self, key, value)
        return value
