from fastapi import APIRouter as Router

from cookiecutter_fastAPI_v2.core.base.app import BaseResponse, format_response

routers = []


class APIRouter(Router):
    def __init__(self, *args, **kwargs):
        super(APIRouter, self).__init__(*args, **kwargs)
        routers.append(self)

    def api_route(self, *args, **kwargs):
        # 序列化全局返回值
        if 'response_model' in kwargs:
            if not issubclass(kwargs['response_model'], BaseResponse):
                kwargs['response_model'] = format_response(kwargs['response_model'])
        return super(APIRouter, self).api_route(*args, **kwargs)

index_router = APIRouter(
    prefix="",
    tags=["index"],
)

auth_v1_router = APIRouter(
    prefix="/auth/v1",
    tags=["auth"]
)


task_router = APIRouter(
    prefix="/task",
    tags=["task"],
)