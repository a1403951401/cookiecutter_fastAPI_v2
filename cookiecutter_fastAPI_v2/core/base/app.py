import typing

from fastapi import FastAPI
from fastapi.datastructures import Default
from fastapi.responses import Response
from pydantic import create_model
from pydantic.generics import GenericModel
from tortoise import Tortoise

from cookiecutter_fastAPI_v2.config import config
from cookiecutter_fastAPI_v2.utils import dumps


class ORJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return dumps(content, decode=False)


DataT = typing.TypeVar('DataT')


class BaseResponse(GenericModel, typing.Generic[DataT]):
    code: int = 200
    message: str = 'ok'
    data: typing.Optional[DataT] = None


def init_error_response(cls: typing.Type[Exception]) -> typing.Type[Exception]:
    cls.model = create_model(
        cls.__name__ + "Model",
        code=getattr(cls, 'code', 500),
        message=getattr(cls, 'message', '方法内部错误'),
        __base__=BaseResponse,
    )
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
