import inspect
import typing

from fastapi import FastAPI
from fastapi.datastructures import Default
from fastapi.responses import Response, ORJSONResponse
from tortoise import Tortoise

from cookiecutter_fastAPI_v2.config import config
from cookiecutter_fastAPI_v2.utils import dumps, BaseModel
from cookiecutter_fastAPI_v2.utils.context import context


class ORJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return dumps(content, decode=False)


class BaseResponse(BaseModel):
    code: int = 200
    message: str = 'ok'
    data: typing.Any = None

    def __init__(self, **kwargs):
        super(BaseResponse, self).__init__(**kwargs)

    @property
    def response(self) -> ORJSONResponse:
        return ORJSONResponse(self)


BASE_ATTR_NAME = [attr_name for attr_name, _ in inspect.getmembers(BaseModel)]


def format_response(cls: typing.Type[BaseModel]) -> typing.Type[typing.Type[BaseResponse]]:
    response_name = cls.__name__
    cls.__name__ += "Data"

    class T(BaseResponse):
        data: cls = None

    def __init__(self, **kwargs):
        super(T, self).__init__(**{
            'code': context.code,
            'message': context.message,
            'data': kwargs,
        })

    t = type(response_name, (T,), {'__init__': __init__})
    return t


def init_error_response(cls: typing.Type[Exception]) -> typing.Type[Exception]:
    class T(BaseResponse):
        code: int = getattr(cls, 'code', 500)
        message: str = getattr(cls, 'message', '方法内部错误')

    cls.model = type(cls.__name__ + "Model", (T,), {})
    app.router.responses[getattr(cls, 'code', 500)] = {'model': cls.model}
    return cls


app = FastAPI(
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None,
    openapi_url="/openapi.json" if config.DEBUG else None,
    version=config.RELEASE,
    default_response_class=Default(ORJSONResponse),
)

# 初始化数据库模型
Tortoise.init_models(["cookiecutter_fastAPI_v2.core.auth.models"], "models")
