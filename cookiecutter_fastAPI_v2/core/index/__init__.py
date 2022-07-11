from cookiecutter_fastAPI_v2.config import config
from cookiecutter_fastAPI_v2.core.base.app import BaseResponse
from cookiecutter_fastAPI_v2.core.base.router import index_router
from cookiecutter_fastAPI_v2.utils import BaseModel
from cookiecutter_fastAPI_v2.utils.context import context


class PongResponse(BaseModel):
    tag: str | None = config.TAG
    release: str | None = config.RELEASE
    ping: int | None = None


@index_router.get("/ping",
                  summary="测试接口",
                  description='测试服务端是否正常，并返回 tag 以及 release',
                  response_model=BaseResponse[PongResponse])
async def ping() -> BaseResponse[PongResponse]:
    context.message = 'pong'
    return BaseResponse[PongResponse](
        data=PongResponse(ping=await context.redis.incr('ping') if context.redis else None))
