from contextvars import ContextVar

from arq import ArqRedis
from redis.asyncio.client import Redis

from cookiecutter_fastAPI_v2.core.auth.models import User
from cookiecutter_fastAPI_v2.utils import BaseModel


class Auth(BaseModel):
    is_auth: bool = False
    user: User.models() | None = None
    permission: set = set()


class Context:
    _auth = ContextVar('auth', default=Auth())
    pool: ArqRedis = None
    redis: Redis = None

    _code = ContextVar('code', default=200)
    _message = ContextVar('message', default='ok')

    @property
    def auth(self) -> Auth:
        return self._auth.get()

    @auth.setter
    def auth(self, auth: Auth):
        self._auth.set(auth)

    @property
    def code(self) -> int:
        return self._code.get()

    @code.setter
    def code(self, code: int):
        self._code.set(code)

    @property
    def message(self) -> str:
        return self._message.get()

    @message.setter
    def message(self, message: str):
        self._message.set(message)


context = Context()
