from typing import Type

from pydantic.main import ModelMetaclass
from tortoise import Model
from tortoise.contrib.pydantic import PydanticModel
from tortoise.queryset import QuerySet

from cookiecutter_fastAPI_v2.core.auth.models import User
from cookiecutter_fastAPI_v2.core.base.router import auth_v2_router
from cookiecutter_fastAPI_v2.utils.cbv import CBV
from cookiecutter_fastAPI_v2.utils.cbv.const import QUERYSET_AUTO_MODEL_READONLY


class TestCBV(CBV):

    async def post(self, obj: Model):
        model: Type[PydanticModel] = self.get_meta(QUERYSET_AUTO_MODEL_READONLY)
        data = model.from_orm(obj)
        data.username += '_copy'
        return await self.model.create(**data.dict())

    async def put(self, data: ModelMetaclass, obj: Model):
        data.password = User.get_password(data.password)
        return await super().put(data, obj)

    async def put_list(self, data: ModelMetaclass, query: QuerySet):
        data.password = User.get_password(data.password)
        return await super().put_list(data, query)

    class Meta:
        router = auth_v2_router
        resource_name = '/'
        queryset = User
        fields = {
            'username': str
        }
        limit = 50
        offset = 0

        allowed_methods = ['get', 'post', 'delete', 'put']
