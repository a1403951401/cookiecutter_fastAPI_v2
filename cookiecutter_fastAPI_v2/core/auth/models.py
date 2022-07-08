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
    name = fields.CharField(max_length=32, description='角色名')
    description = fields.TextField(null=True, description='角色详情')
    is_admin = fields.BooleanField(default=False, description='是否管理员')
    permission = fields.JSONField(default=list, description='权限')


class User(IDModel):
    """User"""
    username: str = fields.CharField(max_length=64, unique=True, description='用户名')
    password: str | None = fields.CharField(max_length=128, null=True, description='密码hash')
    roles: fields.ManyToManyRelation[Role] = fields.ManyToManyField('models.Role', description='权限')

    # OBJ: UserObj = UserObj

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
    user = fields.ForeignKeyField('models.User', null=True, description='用户')
    source = fields.CharField(max_length=32,
                              choices=const.TOKEN_SOURCE, description='token来源')
    expire_at = fields.DatetimeField(null=True, description='过期时间')
    is_delete = fields.BooleanField(default=False, description='是否失效')
    permission = fields.JSONField(default=list, description='权限')
    created_by = fields.ForeignKeyField('models.User', null=True, related_name='token_created_by', description='创建人')

    @classmethod
    async def create_token(cls, created_by: User, source: str, user: User = None, permission: list | set = None,
                           expire_at: datetime = None):
        if not permission:
            permission = await user.permission if user else await created_by.permission
        return await Token.create(
            user=user,
            source=source,
            permission=list(permission),
            expire_at=expire_at,
            created_by=created_by)
