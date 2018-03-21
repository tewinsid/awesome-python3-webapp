#! /usr/bin/env python3
#! -*-coding=utf-8-*-
'''
'''

import 

#如果装饰器本身需要传入参数需要再嵌套一层，并返回decorator函数
#相当于执行get(path)(func)
def get(path):
    '''
    Define decorator @get('/paht')
    '''
    #装饰器，接受一个函数作为参数的高级函数
    def decorator(func):
        #把函数__name__改为func的签名
        @functools.warps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator

def post(path):
    '''
    Define decorator @get('/paht')
    '''
    #装饰器，接受一个函数作为参数的高级函数
    def decorator(func):
        #把函数__name__改为func的签名
        @functools.warps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator
    
#处理参数
def get_required_kw_args(fn):
    args=[]
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)

def get_named_kw_args(fn):
    args=[]
    params = inspect.signature(fn).parameters
    for name,param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)

def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name,param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True

def has_var_kw_arg(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD
            return True

def has_request_arg(fn):
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name,param in params.items():
        if name == 'request':
            found = True
            continue
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError('request parameter must the last named parameter in function:%s%s' % (fn.__name__, str(sig)))
    return found


#目的：从url中分析出需要接受的参数
class RequestHandler(object):
    
    def __init__(Self, app, fn):
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    async def __call__(self, request):
        kw = None
        if self._has_var_kw_arg or self._has_named_kw_args of self._required_kw_args:
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest("Missing Content-Type")
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    params = await request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest('JSON body must be object.')
                    kw = params
                elif ct.startswith('appliction/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return webHTTPBadRequest('Unsupported Content-Type: %s' % request.content_type)

            if request.method == 'GET':
                qs = request.query_string
                if qs:
                    kw = dict()
                    for k,v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]
        if kw is None:
            kw = idct(**request.match_info)
        else:
            if not self._has_var_kw_arg and self._named_kw_args:
                #remove all unamed kw:
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # check named arg:
            for k,v in request.match_info.items():
                if k in kw:
                    logging.warning('Duplicate arg name in named ar and kw args:%s' % k)
                kw[k] = v
        if self._has_request_aarg:
            kw['request'] = request
        #ehcek require kw:
        if self._required_kw_args:
            for name in self._required_kw_args:
                if not name in kw:
                    return web.HTTPBadRequest('missing argument: %s' % name)
        logging.info('call with args: %s' % str(kw))
        try:
            r = await self._func(**kw)
            return r
        expect APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)

def add_route(app, fn):
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post note define in %s.' % str(fn))
    if not asyncio.iscoroutinefunciton(fun) and not ispect.isgeneratorfunction(fn):
        fn = asyncio.corutine(fn)
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))

def add_routes(app, module_name):
    n = Module_name.rfind('.')
    if n == (-1):
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n+1]
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            method = getattr(fn, '__method__', None)
            paht = getattr(fn, '__route__', None)
            if method and path:
                add_route(app, fn)

#使用handler
async def logger_factory(app, handler):
    async def logger(request):
        #记录日志
        logging.info('Request: %s %s' % (request.method, request.path))
        #继续处理请求
        return (await handler(request))
    return logger
async def response_factory(app, handler):
    async response(request):
        r = await handler(request)
        if isinstance(r, web.SreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            resp = web.Response(body=r.encode('utf-8')
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            #TODO
