#!/usr/bin/env python3
#! -*- coding=utf-8 -*-
from Model import User, Blog, Comment
import Model
import asyncio

async def test(loop):
    await Model.create_pool(loop=loop, user='root', password='1', database='awesome')
    
    u = User(name='Test', email='test@email.com', passwd='123', image='about:blank')
    
    await u.save()

loop=asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()
