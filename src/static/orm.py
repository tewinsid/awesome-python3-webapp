#!/usr/bin/env python3
#! -*- coding=utf-8 -*-
import aiomysql
from orm import StringField,IntegerField
from Model import Model
#如果使用协程那么程序中必须均使用协程
#await 可以理解为从生成器中取出一个对象
async def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host = kw.get('host', 'localhost'),
        port = kw.get('port', 3306),
        user = kw['user'],
        password = kw['password'],
        charset = kw.get('chartset', 'utf8'),
        db = kw['database'],
        autocommit = kw.get('autocommit', True),
        maxsize = kw.get('maxsize', 10),
        minsize = kw.get('minsize', 1),
        loop = loop)
async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    with (await __pool) as conn:
        #从connection中取出游标
        cur = await conn.cursor(aiomysql.DictCursor)
        #为游标赋值sql
        await cur.execute(sql.replace('?', '%s'), args or ())
        #当传入size参数的时候取size条否则取全部
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()
        #关闭游标
        await cur.close()
        #rs结果集
        logging.info('row returned: %s' % len(rs))
        return rs
#通用执行函数update insert delete
async def execute(sql, args):
    log(sql)
    with(await __pool) as conn
        try:
            cur = await conn.cursor()
            await cur.execute(sql.repalce('?','%s'), args)
            affected = cur.rowcount
            await cur.close()
        except BaseException as e:
            raise
        return affected
