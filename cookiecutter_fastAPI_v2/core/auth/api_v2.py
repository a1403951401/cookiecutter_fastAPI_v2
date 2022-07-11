from cookiecutter_fastAPI_v2.core.auth.api_models import UserResponse
from cookiecutter_fastAPI_v2.core.auth.models import User
from cookiecutter_fastAPI_v2.core.base.router import auth_v2_router
from cookiecutter_fastAPI_v2.utils.cbv import CBV, api_route


class TestCBV(CBV):
    @api_route(summary="注册用户")
    async def post_list(self, data):
        return await super(TestCBV, self).post_list(data)

    class Meta:
        router = auth_v2_router
        resource_name = '/'
        queryset = User
        fields = {
            'username': str
        }
        limit = 50
        offset = 0

        allowed_methods = ['get', 'post']
