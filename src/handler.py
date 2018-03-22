#!/usr/env/bin python3
#!-*-coding=utf-8-*-
'''
'''
import re,time,json,logging,base64,asyncio
from coreweb import get,post
from models import User, Comment, Blog, next_id
@get('/')
async def index(request):
    users = User.findAll()
    return {
        '__template__' : 'test.html',
        'users' : users
    }
