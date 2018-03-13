#!/usr/bin/env python3
#! -*- coding=utf-8 -*-

import logging
import time, uuid
from Field import Field
from Field import StringField, BooleanField, FloatField, TextField

def create_args_string(num):
    l=[]
    for n in range(num):
        l.append('?')
    return ', '.join(l)
def log(sql, args=()):
    logging.info('SQL:%s' % sql)
#元类 动态创建类
class ModelMetaclass(type):
    
    #cls 当前准备创建类的对象 attrs 类的方法的集合
    #name 类名 bases 类继承的父类的集合 
    #双下划线开头 私有变量
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        #获取table名
        tableName = attrs.get('__table__', None) or name
        logging.info('found model: %s (table:%s)' % (name, tableName))
        #获取所有Field和主键名
        mappings = dict() # 所有属性
        fields = [] # 除主键外所有字段
        primaryKey = None
        for k,v in attrs.items():
            if isinstance(v, Field):
                logging.info('  found mapping: %s --> %s' % (k, v))
                mappings[k] = v
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError('duplicte primary key for field:%s ' %k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError('primary key not found')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '‘%s’' % f, fields))
        attrs['__mappings__'] = mappings # 保存属性和列的映射关系
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey # 主键属性名
        attrs['__fields__'] = fields # 除主键外的属性名
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ','.join(escaped_fields), tableName)
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ','.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values `%s`' % (tableName, ','.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs) 
class Model(dict, metaclass=ModelMetaclass):
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
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1) 
    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('faield to insert record: affected rows %s' % rows)
def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)
class User(Model):
    __table__ = 'users'
    
    id = StringField(primary_key=True, default=next_id, dll='varchar(50)')
    email = StringField(dll='varchar(50)')
    passwd = StringField(dll='varchar(50)')
    admin = BooleanField()
    name = StringField(dll='varchar(50)')
    image = StringField(dll='varchar(500)')
    create_at = FloatField(default=time.time)

class Blog(Model):
    __table__ = 'blogs'
    
    id = StringField(primary_key=True, default=next_id, dll='varchar(50)')
    user_id = StringField(dll='varchar(50)')
    user_name = StringField(dll='varchar(50)')
    user_image = StringField(dll='varchar(500)')
    name = StringField(dll='varchar(50)')
    summary = StringField(dll='varchar(200)')
    content = TextField()
    create_at = FloatField(default=time.time)
class Comment(Model):
    __table__ = 'commons'
    id = StringField(primary_key=True, default=next_id, dll='varchar(50)')
    blog_id = StringField(dll='varchar(50)')
    user_id = StringField(dll='varchar(50)')
    user_name = StringField(dll='varchar(50)')
    user_image = StringField(dll='varchar(500)')
    content = TextField()
    create_at = FloatField(default=time.time)
