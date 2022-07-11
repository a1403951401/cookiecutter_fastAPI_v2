from fastapi import APIRouter as Router

routers = []
RESPONSE_MAP = {}


class APIRouter(Router):
    def __init__(self, *args, **kwargs):
        super(APIRouter, self).__init__(*args, **kwargs)
        routers.append(self)


index_router = APIRouter(
    prefix="",
    tags=["index"],
)

task_router = APIRouter(
    prefix="/task",
    tags=["task"],
)

auth_v1_router = APIRouter(
    prefix="/auth/v1",
    tags=["auth"]
)

auth_v2_router = APIRouter(
    prefix="/auth/v2",
    tags=["auth"]
)
