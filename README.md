## cookiecutter_fastAPI_V2

> 这只是一个基于 Python 3.10+ 的 fastAPI 快速开发脚手架，包含异步、定时模块

### 相关文档

> https://github.com/mjhea0/awesome-fastapi

### 相关包

- fastapi = 0.78.0 -> uvloop 可以使 asyncio 更快
- uvicorn[standard] = 0.17.6 -> ASGI
- orjson = 3.6.8 -> json 序列化提速
- loguru = 0.6.0 -> 日志
- httpx = 0.23.0 -> asyncio requests
- arq = 0.23a1 -> task、cron 相关异步功能组件
- aioredis = 2.0.1 -> asyncio redis
- tortoise-orm[asyncpg] = 0.19.1 -> asyncio orm
- aerich = 0.6.3 -> migration
- passlib = 1.7.4 -> hash
- async-property = 0.2.1 -> @async_property
- typing-extensions = 4.2.0 -> typing
- aioredis = 2.0.1 -> asyncio redis

### 启动服务

> docker-compose up

#### [「docs」 /docs](http://127.0.0.1:8080/docs)

#### [「redoc」 /redoc](http://127.0.0.1:8080/redoc)

### 关于 orm

> 协程服务中不建议使用同步组件，如使用 sqlalchemy 在使用 psycopg2 / psycopg2-binary 请注意以下问题

#### ARM 用户须知「包括 MAC 用户」

> 由于 libpg 上游的存在一个错误可能会出现以下报错，因此建议用户通过 x86 架构来开发、运行脚手架
>
> SCRAM authentication requires libpq version 10 or above
>
> 来源： https://github.com/psycopg/psycopg2/issues/1360
>
> 在 psycopg2 fix 该问题之前，建议 MAC 用户通过 [Rosetta](https://docs.docker.com/desktop/mac/apple-silicon/) 运行『注意，该方式会影响性能」

