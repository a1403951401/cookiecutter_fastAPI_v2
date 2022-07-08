import typing

from fastapi import Cookie

from cookiecutter_fastAPI_v2.core.auth.models import Token
from cookiecutter_fastAPI_v2.core.base.exceptions import AccessTokenExpire, ForbiddenError
from cookiecutter_fastAPI_v2.utils.context import context, Auth


def auth_user(auth: bool | str | list = True, need_user=True) -> typing.Callable:
    """ 校验用户路由权限 """

    async def check_permission(token: str = Cookie(None, title="用户 token")) -> 'Auth':

        token = await Token.filter(id=token).first()
        user = await token.user if token else None
        context.auth = Auth(
            is_auth=bool(token),
            is_admin=await user.is_admin if user else False,
            user=user,
            permission=token.permission if token else set(),
            token=token)
        # 非认证接口直接返回
        if not auth:
            return context.auth
        # 认证接口必须有 token
        if not token:
            raise AccessTokenExpire()
        # 需要用户 user 的场景必须读取到 user
        if need_user and not user:
            raise ForbiddenError()
        # 通用型授权接口
        if auth is True:
            return context.auth
        # 必须包含其中一个权限才允许访问
        if context.auth.permission & set([auth] if isinstance(auth, str) else auth):
            return context.auth
        raise ForbiddenError()

    return check_permission
