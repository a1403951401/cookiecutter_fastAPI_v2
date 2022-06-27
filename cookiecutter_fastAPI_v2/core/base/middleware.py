from time import time
from uuid import uuid4

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

middlewares = []


def add_wrapper(cls):
    def wrapper(*args, **kwargs):
        return cls(*args, **kwargs)

    middlewares.append((getattr(cls, 'name', None) or cls.__name__, cls))
    return wrapper


@add_wrapper
class TraceMiddleware(BaseHTTPMiddleware):
    """ 添加回溯信息 """
    name: str = 'trace'
    app: ASGIApp

    async def dispatch(self, request, call_next):
        before = time()
        trace_data = {
            'Ts-Request-Id': request.headers.get('Ts-Request-Id', str(uuid4())),
        }
        with logger.contextualize(**trace_data):
            response: Response = await call_next(request)
        after = time()
        response.headers.update({
            'X-Request-After': str(after),
            'X-Request-Before': str(before),
            'X-Response-Time': str(after - before),
            **trace_data
        })
        return response
