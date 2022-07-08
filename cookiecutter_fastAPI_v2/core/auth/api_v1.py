import datetime

from cookiecutter_fastAPI_v2 import const
from cookiecutter_fastAPI_v2.core.auth.api_models import UserResponse, UserRequest, get_user_response
from cookiecutter_fastAPI_v2.core.auth.models import User, Role, Token
from cookiecutter_fastAPI_v2.core.base.app import ORJSONResponse
from cookiecutter_fastAPI_v2.core.base.exceptions import BadResponse, AccessTokenExpire
from cookiecutter_fastAPI_v2.core.base.router import auth_v1_router


@auth_v1_router.post("/register",
                     summary="用户注册",
                     response_model=UserResponse)
async def register(data: UserRequest) -> ORJSONResponse:
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
async def login(data: UserRequest) -> ORJSONResponse:
    user = await User.filter(username=data.username).first()
    if not user or not user.check_password(data.password):
        raise AccessTokenExpire()
    expire_at = datetime.datetime.now() + const.TOKEN_MAX_AGE
    token: Token = await Token.create_token(
        user=user,
        created_by=user,
        source=const.TOKEN_SOURCE_LOGIN,
        expire_at=expire_at)
    rsp = await get_user_response(user, token=token.id)
    rsp.set_cookie('token', token.id, expires=const.TOKEN_MAX_AGE.total_seconds())
    rsp.set_cookie('username', user.username, expires=const.TOKEN_MAX_AGE.total_seconds())
    return rsp
