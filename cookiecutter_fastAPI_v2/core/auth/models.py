from datetime import datetime

import bcrypt
from async_property import async_property
from tortoise import fields

from cookiecutter_fastAPI_v2 import const
from cookiecutter_fastAPI_v2.config import config
from cookiecutter_fastAPI_v2.core.auth.objects import UserObj
from cookiecutter_fastAPI_v2.core.base.mixin import IDModel, UUIDModel
from cookiecutter_fastAPI_v2.core.base.permission import PERMISSION_MAP


class Role(IDModel):
    """ Role """
    name = fields.CharField(max_length=32)
    description = fields.TextField(null=True)
    is_admin = fields.BooleanField(default=False)
    permission = fields.JSONField(default=list)


class User(IDModel):
    """User"""
    username: str = fields.CharField(64)
    password: str | None = fields.CharField(128, null=True)
    roles: fields.ManyToManyRelation[Role] = fields.ManyToManyField('models.Role')

    OBJ: UserObj = UserObj

    async def set_password(self, password: str):
        self.password = bcrypt.hashpw(password.encode('utf-8'), config.DB_SALT).decode('utf-8')
        await self.save(update_fields=['password'])

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    @async_property
    async def is_admin(self) -> bool:
        return await self.roles.filter(is_admin=True).exists()

    @async_property
    async def permission(self) -> set:
        if await self.is_admin:
            return set(PERMISSION_MAP.keys())
        permission = set()
        async for role in self.roles.all():
            permission |= set(role.permission)
        return permission

    class PydanticMeta:
        exclude = ["password_hash"]


class Token(UUIDModel):
    user = fields.ForeignKeyField('models.User')
    source = fields.CharField(max_length=32,
                              choices=const.TOKEN_SOURCE)
    expire_at = fields.DatetimeField(null=True)
    is_delete = fields.BooleanField(default=False)
    permission = fields.JSONField(default=list)

    @classmethod
    async def create_token(cls, user: User, source: str, permission: list | set = None, expire_at: datetime = None):
        if not permission:
            permission = await user.permission
        return await Token.create(
            user=user,
            source=source,
            permission=list(permission),
            expire_at=expire_at)
