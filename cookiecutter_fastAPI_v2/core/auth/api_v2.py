from cookiecutter_fastAPI_v2.core.auth.api_models import UserResponse
from cookiecutter_fastAPI_v2.core.auth.models import User
from cookiecutter_fastAPI_v2.core.base.router import auth_v2_router
from cookiecutter_fastAPI_v2.utils.cbv import CBV, api_route


class TestCBV(CBV):
    async def dehydrate(self, obj: User, for_list: bool = False) -> UserResponse:
        return UserResponse(id=obj.id, username=obj.username)

    @api_route(summary="查询用户")
    async def get(self, obj):
        return await super(TestCBV, self).get(obj)

    @api_route(summary="批量查询用户")
    async def get_list(self, query):
        return await super(TestCBV, self).get_list(query)

    class Meta:
        router = auth_v2_router
        resource_name = '/'
        queryset = User
        fields = {
            'username': str
        }
        limit = 50
        offset = 0

        allowed_methods = ['get']
