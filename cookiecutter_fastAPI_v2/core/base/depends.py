import typing

from fastapi import Cookie

from cookiecutter_fastAPI_v2.core.auth.models import Token
from cookiecutter_fastAPI_v2.core.base.exceptions import AccessTokenExpire, ForbiddenError


def auth_user(auth: bool | str | list = True) -> typing.Callable:
    """ 校验用户路由权限 """

    async def check_permission(token: str = Cookie(None, title="用户 token")) -> 'Auth':
        from cookiecutter_fastAPI_v2.utils.context import context, Auth

        token = await Token.filter(id=token).first()
        context.auth = Auth(
            is_auth=bool(token),
            user=await token.user if token else None,
            permission=await token.permission if token else set())
        # 非认证接口直接返回
        if not auth:
            return context.auth
        if not context.auth.user:
            raise AccessTokenExpire()
        # 通用型授权接口
        if auth is True:
            return context.auth
        # 必须包含其中一个权限才允许访问
        if context.auth.permission & set([auth] if isinstance(auth, str) else auth):
            return context.auth
        raise ForbiddenError()

    return check_permission
