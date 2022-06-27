import datetime

from fastapi import Depends

from cookiecutter_fastAPI_v2 import const
from cookiecutter_fastAPI_v2.core.auth.models import User, Role, Token
from cookiecutter_fastAPI_v2.core.base.app import ORJSONResponse
from cookiecutter_fastAPI_v2.core.base.depends import auth_user
from cookiecutter_fastAPI_v2.core.base.exceptions import BadResponse, AccessTokenExpire
from cookiecutter_fastAPI_v2.core.base.router import auth_v1_router
from cookiecutter_fastAPI_v2.utils import BaseModel


class UserResponse(BaseModel):
    username: str
    is_admin: bool = False
    permission: set = set()


async def get_user_response(user: User) -> UserResponse | ORJSONResponse:
    return ORJSONResponse(
        UserResponse(
            username=user.username,
            is_admin=await user.is_admin,
            permission=await user.permission,
        ))


class Auth(BaseModel):
    username: str
    password: str


@auth_v1_router.post("/register",
                     summary="用户注册",
                     response_model=UserResponse)
async def register(data: Auth) -> UserResponse:
    if await User.filter(username=data.username).exists():
        raise BadResponse(message='user %s is exists' % data.username)

    user = await User.create(username=data.username)
    await user.set_password(data.password)

    if not await Role.exists():
        role = await Role.create(name='admin', is_admin=True)
        await user.roles.add(role)
    return await get_user_response(user)


@auth_v1_router.post("/login",
                     summary="用户登录",
                     response_model=UserResponse)
async def login(data: Auth) -> UserResponse:
    user = await User.filter(username=data.username).first()
    print(user.object)
    if not user or not user.check_password(data.password):
        raise AccessTokenExpire()
    expire_at = datetime.datetime.now() + const.TOKEN_MAX_AGE
    token = await Token.create_token(
        user,
        source=const.TOKEN_SOURCE_LOGIN,
        expire_at=expire_at
    )
    rsp = await get_user_response(user)
    rsp.set_cookie('token', token.id, expires=const.TOKEN_MAX_AGE.total_seconds())
    rsp.set_cookie('username', user.username, expires=const.TOKEN_MAX_AGE.total_seconds())
    return rsp


@auth_v1_router.put("/{user_id}",
                    summary="用户修改密码",
                    response_model=UserResponse)
async def update_password(
        user: User = Depends(auth_user(True)),
        user_id: int = None) -> UserResponse:
    return await get_user_response(user)
