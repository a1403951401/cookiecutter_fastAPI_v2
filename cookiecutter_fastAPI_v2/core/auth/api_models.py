from uuid import UUID

from cookiecutter_fastAPI_v2.core.auth.models import User
from cookiecutter_fastAPI_v2.core.base.app import ORJSONResponse, BaseResponse
from cookiecutter_fastAPI_v2.utils import BaseModel


class UserRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str
    is_admin: bool = False
    permission: set = set()
    token: UUID = None


async def get_user_response(user: User, token: str = None) -> ORJSONResponse:
    return ORJSONResponse(
        BaseResponse(data=UserResponse(
            username=user.username,
            is_admin=await user.is_admin,
            permission=await user.permission,
            token=token,
        )))
