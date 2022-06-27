import pkgutil
from importlib import import_module

from fastapi import HTTPException as FHTTPException
from fastapi.exceptions import RequestValidationError
from redis.asyncio import Redis
from starlette.exceptions import HTTPException as SHTTPException
from tortoise import Tortoise

from cookiecutter_fastAPI_v2.core.base.app import app
from cookiecutter_fastAPI_v2.core.base.exceptions import exception_handler
from cookiecutter_fastAPI_v2.core.base.middleware import middlewares
from cookiecutter_fastAPI_v2.core.base.router import routers
from cookiecutter_fastAPI_v2.utils import *
from cookiecutter_fastAPI_v2.utils.arq import Worker
from cookiecutter_fastAPI_v2.utils.context import context


def import_paths(*module_list: str):
    """ 由于使用递归导入的方法，文件夹须通过 __init__.py 声明该目录为包 """
    for filefiner, name, ispkg in pkgutil.iter_modules([str(config.PROJECT_PATH.joinpath(*module_list))]):
        import_paths(*module_list, name)
        if import_module(".".join([config.PROJECT_NAME, *module_list, name])):
            logger.debug(f"import {'.'.join([config.PROJECT_NAME, *module_list, name])}")


# 载入
for name, path in config.PATH.items():
    logger.debug(f"import {name} models: {config.PROJECT_NAME}.{path.replace('/', '.')}")
    import_paths(*(path.split('/')))

# 载入异常处理
EXCEPTION_LOG_HANDLER = (Exception, FHTTPException, SHTTPException, RequestValidationError)
for e in EXCEPTION_LOG_HANDLER:
    app.add_exception_handler(e, exception_handler)
    logger.debug(f"add exception handler {e.__module__}.{e.__name__}")

# 载入路由
for router in routers:
    app.include_router(router)
    logger.debug(f"include router {router.prefix}")

# 载入中间层「倒叙排列，从上到下依次载入中间层」
for name, middleware in middlewares[::-1]:
    app.add_middleware(middleware)
    logger.debug(f"add middleware {name}")


# 载入启动事件
@app.on_event("startup")
async def startup():
    """ https://tortoise.github.io/query.html """
    orm = await Tortoise.init(
        db_url=config.DB_DSN,
        modules={
            'models': config.DB_MODELS
        }
    )
    await Tortoise.generate_schemas(safe=True)
    logger.debug(f'init tortoise: {Tortoise._inited}')
    context.pool = await Worker.create_pool()
    logger.debug(f'init worker: {await context.pool.ping()}')
    context.redis = Redis.from_url(url=config.REDIS_DSN)
    logger.debug(f'init pool: {await context.redis.ping()}')


@app.on_event("shutdown")
async def shutdown():
    pass
