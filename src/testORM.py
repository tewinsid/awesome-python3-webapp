#!/usr/bin/env python3
#! -*- coding=utf-8 -*-
from orm import User, Blog, Comment
import orm
import asyncio

async def test(loop):
    await orm.create_pool(loop=loop, user='root', password='1', db='awesome')
    
    u = User(name='tewinsdi', email='tewisid@email.com', passwd='123', image='about:blank')
    
    await u.save()

loop=asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()
