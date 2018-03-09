#!/usr/bin/env python3
#! -*- coding=utf-8 -*-
‘’‘
’‘’
import orm
from Model import User, Blog, Comment

def test():
    await orm.create_pool(user='root', password='1', database='awesome')
    
    u = User(name='Test', email='test@email.com', passwd='123', image='about:blank')
    
    await u.save()

for x in test():
    pass 
