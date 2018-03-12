#!/usr/bin/env python3
#! -*- coding=utf-8 -*-
class Field(object):
    
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s,%s:%s>' % (self.__class__.__name__, self.column_type, self.name)

class StringField(Field):
    
    def __init__(self, name=None, primary_key=False, default=None, dll='varchar(100)'):
        super().__init__(name, dll, primary_key, default)

class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=None, dll='char(1)'):
        super().__init__(name, dll, primary_key, default)

class TextField(Field):
    def __init__(self, name=None, primary_key=False, default=None, dll='varchar(400)'):
        super().__init__(name, dll, primary_key, default)

class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=None, dll='int'):
        super().__init__(name, dll, primary_key, default)
