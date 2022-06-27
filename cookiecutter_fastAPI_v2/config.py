import os
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import BaseSettings, Field, validator, PostgresDsn, RedisDsn


def popen(cmd: str) -> str:
    try:
        return os.popen(cmd).read().replace('\n', '')
    except:
        return ''


class Config(BaseSettings):
    # 基础配置
    DEBUG: bool = True
    PROJECT_PATH: Path = Path(__file__).parent.resolve()
    PROJECT_NAME: str = PROJECT_PATH.name

    # 分支
    TAG: str = None
    RELEASE: str = None

    # 时区
    TIME_ZONE: str = Field('Asia/Shanghai', env='TZ')

    # 数据库
    DB_SCHEMES: str = 'postgres'
    DB_HOST: str = 'postgres'
    DB_PORT: int = 5432
    DB_USERNAME: str = 'postgres'
    DB_PASSWORD: str = 'postgres'
    DB_TABLE: str = 'cookiecutter_fastAPI'
    DB_DSN: PostgresDsn
    DB_MODELS = ["cookiecutter_fastAPI_v2.core.auth.models"]
    DB_SALT: bytes = None

    @property
    def PATH(self):
        """ 默认的引入路径 """
        return {
            'view': 'core',
            'task': 'worker/task',
            'cron': 'worker/cron',
        }

    @property
    def DB_DSN(self) -> PostgresDsn:
        return PostgresDsn(f"{self.DB_SCHEMES}://"
                           f"{quote_plus(self.DB_USERNAME)}:{quote_plus(self.DB_PASSWORD)}@"
                           f"{quote_plus(self.DB_HOST)}:{self.DB_PORT}/"
                           f"{quote_plus(self.DB_TABLE)}", scheme=self.DB_SCHEMES)

    @property
    def CELERY_DSN(self) -> str:
        return f'db+postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}@' \
               f'{self.DB_HOST}:{self.DB_PORT}/' \
               f'{self.DB_TABLE}'

    AUTH_WHITE_LIST = [
        '/'
    ]

    @validator('DB_SALT')
    def set_db_salt(cls, v, values, **kwargs):
        return v or values['DB_TABLE'].encode('utf-8')

    DB_COMMIT: int = 100

    # redis
    REDIS_SCHEMES: str = 'redis'
    REDIS_PASSWORD: str = None
    REDIS_HOST: str = 'redis'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_SOCKET_TIMEOUT: str = None
    REDIS_DSN: RedisDsn

    @property
    def REDIS_DSN(self) -> RedisDsn:
        return RedisDsn(f"{self.REDIS_SCHEMES}://"
                        f"{quote_plus(self.REDIS_HOST)}:{self.REDIS_PORT}/"
                        f"{self.REDIS_DB}", scheme=self.REDIS_SCHEMES)

    WORKER_KEEP = 60 * 60
    WORKER_DB = 1

    @property
    def WROKER_DSN(self) -> RedisDsn:
        return RedisDsn(f"{self.REDIS_SCHEMES}://"
                        f"{quote_plus(self.REDIS_HOST)}:{self.REDIS_PORT}/"
                        f"{self.WORKER_DB}", scheme=self.REDIS_SCHEMES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TAG = popen('git tag')
        self.RELEASE = popen('git rev-parse HEAD')


config = Config()

TORTOISE_ORM = {
    "connections": {
        "default": config.DB_DSN
    },
    "apps": {
        "models": {
            "models": ["aerich.models", *config.DB_MODELS],
            "default_connection": "default",
        },
    },
    'timezone': config.TIME_ZONE,
}

if __name__ == '__main__':
    for k, v in config.dict().items():
        print(k, v)
