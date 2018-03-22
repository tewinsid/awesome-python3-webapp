#!/usr/bin/env python3
#! -*- coding=utf-8 -*-

import logging, aiomysql
import time, uuid
from Field import Field
from Field import IntegerField, StringField, BooleanField, FloatField, TextField

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
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'] = mappings # 保存属性和列的映射关系
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey # 主键属性名
        attrs['__fields__'] = fields # 除主键外的属性名
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ','.join(escaped_fields), tableName)
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ','.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
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
        except KeyError:
            #raise AttributeError(r"'Model' object has no attribute '%s'" % key)
            return None
    
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
    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        ' find objects by where clause. '
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        ' find number by select and where. '
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']
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
    created_at = FloatField(default=time.time)

class Blog(Model):
    __table__ = 'blogs'
    
    id = StringField(primary_key=True, default=next_id, dll='varchar(50)')
    user_id = StringField(dll='varchar(50)')
    user_name = StringField(dll='varchar(50)')
    user_image = StringField(dll='varchar(500)')
    name = StringField(dll='varchar(50)')
    summary = StringField(dll='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)
class Comment(Model):
    __table__ = 'commons'
    id = StringField(primary_key=True, default=next_id, dll='varchar(50)')
    blog_id = StringField(dll='varchar(50)')
    user_id = StringField(dll='varchar(50)')
    user_name = StringField(dll='varchar(50)')
    user_image = StringField(dll='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)
async def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host = kw.get('host', 'localhost'),
        port = kw.get('port', 3306),
        user = kw['user'],
        password = kw['password'],
        charset = kw.get('chartset', 'utf8'),
        db = kw['db'],
        autocommit = kw.get('autocommit', True),
        maxsize = kw.get('maxsize', 10),
        minsize = kw.get('minsize', 1),
        loop = loop)
async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    async with __pool.get() as conn:
        #从connection中取出游标
        async with conn.cursor(aiomysql.DictCursor) as cur:
            #为游标赋值sql
            await cur.execute(sql.replace('?', '%s'), args or ())
            #当传入size参数的时候取size条否则取全部
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
                #关闭游标
        #rs结果集
        logging.info('row returned: %s' % len(rs))
        return rs
#通用执行函数update insert delete
async def execute(sql, args, autocommit=True):
    log(sql)
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                print(sql.replace('?','%s'), args) 
                await cur.execute(sql.replace('?','%s'), args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        return affected
