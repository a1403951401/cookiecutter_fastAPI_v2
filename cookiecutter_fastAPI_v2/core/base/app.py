import typing

from fastapi import FastAPI
from fastapi.datastructures import Default
from fastapi.responses import Response, ORJSONResponse
from pydantic import create_model
from pydantic.generics import GenericModel
from tortoise import Tortoise
from tortoise.queryset import QuerySet

from cookiecutter_fastAPI_v2.config import config
from cookiecutter_fastAPI_v2.utils import dumps, BaseModel
from cookiecutter_fastAPI_v2.utils.context import context


class ORJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return dumps(content, decode=False)


DataT = typing.TypeVar('DataT')


class BaseResponse(GenericModel, typing.Generic[DataT]):
    code: int = 200
    message: str = 'ok'
    data: typing.Optional[DataT] = None

    @property
    def response(self) -> ORJSONResponse:
        return ORJSONResponse(self)


class MetaResponse(BaseModel):
    limit: int
    offset: int
    total_count: int

    def __init__(self):
        super(MetaResponse, self).__init__(**{
            'limit': context.limit,
            'offset': context.offset,
            'total_count': context.total_count,
        })


class ListResponseData(GenericModel, typing.Generic[DataT]):
    meta: MetaResponse
    objects: typing.List[DataT]


class ListResponse(BaseResponse, typing.Generic[DataT]):
    data: ListResponseData[DataT]


def init_error_response(cls: typing.Type[Exception]) -> typing.Type[Exception]:
    cls.model = create_model(
        cls.__name__ + "Model",
        code=getattr(cls, 'code', 500),
        message=getattr(cls, 'message', '方法内部错误'),
        __base__=BaseResponse,
    )
    app.router.responses[getattr(cls, 'code', 500)] = {'model': cls.model}
    return cls

async def get_list_response(query: QuerySet, dehydrate: typing.Coroutine):
    pass

app = FastAPI(
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None,
    openapi_url="/openapi.json" if config.DEBUG else None,
    version=config.RELEASE,
    default_response_class=Default(ORJSONResponse),
)

# 初始化数据库模型
Tortoise.init_models(["cookiecutter_fastAPI_v2.core.auth.models"], "models")
