#!/usr/bin/env python3
#! -*- coding=utf-8 -*-
'''

'''
class Field(object):
    
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s,%s:%s>' % (self.__class__.__name__, self.column_type, self.nme)

class StringField(Field):
    
    def __init__(self, name=None, primary_key=False, default=None, dll='varchar(100)'):
        super().__init__(name, dll, primary_key, default)

#元类 动态创建类
class ModelMetaclass(type):
    
    #cls 当前准备创建类的对象 attrs 类的方法的集合
    #name 类名 bases 类继承的父类的集合 
    #双下划线开头 私有变量
    def __new__(cls, name, bases, attrs):
        if name == 'Model'
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
                if v.primary_key
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
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values `%s`' % (tableName, ','.join(escaped_fields), primarykey, create_args_string(len(escaped_fields) + 1))
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        return type.new(cls, name, bases. attrsi) 
