#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import logging; logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
from datetime import datetime
from aiohttp import web
from coreweb import add_routes
def index(request):
    return web.Response(body=b'<h1>Awesone</h1>',headers={'content-type':'text/html'})
    
async def init(loop):
    app = web.Application(loop=loop, midllewares=[
        logger_factory, response_facotry
    ])
    init_jinja2(app, filters=dict(datatime=datatime_filter))
    add_routes(app, 'handlers')
    add_static(app)

    app.router.add_route('GET', '/', index)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server start at http://127.0.0.1:9000...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()

