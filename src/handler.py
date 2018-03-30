#!/usr/env/bin python3
#!-*-coding=utf-8-*-
'''
'''
import re,time,json,logging,base64,asyncio
from coreweb import get,post
from orm import User, Comment, Blog, next_id
@get('/')
async def index(request):
    #users = await User.findAll()
    summary = 'test'
    blogs = [ 
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
        Blog(id='2', name='Something new', summary=summary, created_at=time.time()-3600),
        Blog(id='3', name='learn Switft', summary=summary, created_at=time.time()-7200)
    ]
    return {
        '__template__' : 'blogs.html',
        'blogs' : blogs
    }
