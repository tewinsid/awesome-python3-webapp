#!/usr/bin/env python3
#! -*- coding=utf-8 -*-

import time, uuid
from orm import Model, StringField, BooleanField, FloatField, TextField
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
    @classmethod #查找方法作为类的类方法
    async def find(cls, pk):
        'find object by primary'
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1j	 
    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('faield to insert record: affected rows %s' % rows):
def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)
class User(Model):
    __table__ = 'user'
    
    id = StringField(primary_key=True, defautl=next_id, dll='varchar(50)')
    email = StringField(dll='varchar(50)')
    passwd = StringField(dll='varchar(50)')
    admin = BooleanField()
    name = StringField(dll='varchar(50)')
    image = StringField(dll='varchar(500)')
    create_at = FloatField(default=time.time)

class Blog(Model):
    __table__ = 'blog'
    
    id = StringField(primary_key=True, defautl=next_id, dll='varchar(50)')
    user_id = StringField(dll='varchar(50)')
    user_name = StringField(dll='varchar(50)')
    user_image = StringField(dll='varchar(500)')
    name = StringField(dll='varchar(50)')
    summary = StringField(dll='varchar(200)')
    content = TextField()
    create_at = FloatField(default=time.time)
