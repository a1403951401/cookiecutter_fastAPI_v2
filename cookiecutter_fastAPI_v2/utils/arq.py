import types
import typing
from datetime import datetime
from typing import TypedDict

from arq import Worker as W, ArqRedis
from arq.connections import RedisSettings, create_pool
from arq.cron import CronJob, cron
from arq.typing import OptionType, WeekdayOptionType, SecondsTimedelta
from arq.worker import Function
from tortoise import Tortoise

from cookiecutter_fastAPI_v2.utils import *


class BaseCTX(TypedDict):
    redis: ArqRedis


class CTX(BaseCTX):
    job_id: str
    job_try: int
    enqueue_time: datetime


class Worker(W):
    functions: typing.List[Function | types.CoroutineType] = []
    cron_jobs: typing.List[CronJob] = []

    def __init__(self, is_run=True, **kwargs):
        self.__dict__.update(kwargs)
        if self.functions or self.cron_jobs:
            super().__init__(
                functions=self.functions or [],
                cron_jobs=self.cron_jobs or None,
                on_startup=self.startup,
                on_shutdown=self.shutdown,
                on_job_start=self.on_job_start,
                on_job_end=self.on_job_end,
                redis_settings=RedisSettings().from_dsn(config.WROKER_DSN),
                keep_result=config.WORKER_KEEP
            )
            if is_run:
                self.run()

    @classmethod
    async def create_pool(cls):
        return await create_pool(RedisSettings().from_dsn(config.WROKER_DSN))

    @staticmethod
    async def startup(ctx: BaseCTX):
        """ https://tortoise.github.io/query.html """
        await Tortoise.init(
            db_url=config.DB_DSN,
            modules={
                'models': config.DB_MODELS
            }
        )
        await Tortoise.generate_schemas(safe=True)
        logger.debug('init tortoise')

    @staticmethod
    async def shutdown(ctx: BaseCTX):
        pass

    @staticmethod
    async def on_job_start(ctx: BaseCTX):
        pass

    @staticmethod
    async def on_job_end(ctx: BaseCTX):
        pass

    @classmethod
    def task(cls, func):
        logger.debug(f'register task:{func.__name__}')
        cls.functions.append(func)

    @classmethod
    def cron(cls,
             name: typing.Optional[str] = None,
             month: OptionType = None,
             day: OptionType = None,
             weekday: WeekdayOptionType = None,
             hour: OptionType = None,
             minute: OptionType = None,
             second: OptionType = 0,
             microsecond: int = 123_456,
             run_at_startup: bool = False,
             unique: bool = True,
             timeout: typing.Optional[SecondsTimedelta] = None,
             keep_result: typing.Optional[float] = 0,
             keep_result_forever: typing.Optional[bool] = False,
             max_tries: typing.Optional[int] = 1):
        """ 最低1分钟1次 """

        def wrapper(func):
            logger.debug(f'register worker:{func.__name__}')
            cls.cron_jobs.append(
                cron(func, name=name, month=month, day=day, weekday=weekday, hour=hour, minute=minute,
                     second=second, microsecond=microsecond, run_at_startup=run_at_startup, unique=unique,
                     timeout=timeout, keep_result=keep_result, keep_result_forever=keep_result_forever,
                     max_tries=max_tries)
            )

        return wrapper


if __name__ == '__main__':
    Worker()
