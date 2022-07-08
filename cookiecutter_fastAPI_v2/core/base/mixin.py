import typing
from datetime import datetime

import typing_extensions
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper
from pydantic.utils import ROOT_KEY
from tortoise import fields, Model, BaseDBAsyncClient
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel
from tortoise.queryset import QuerySetSingle

from cookiecutter_fastAPI_v2.utils import BaseModel


class PydanticMixin:
    """ 将 Model 序列化为 Pydantic 模型 """
    id: fields.IntField | fields.UUIDField

    OBJ: typing.Type['PydanticModel'] = None
    AWAIT_OBJ = {}

    @classmethod
    async def obj_dehydrate(obj):
        return obj

    async def object(self, models=None, dehydrate: typing.Coroutine = None):
        """ 自动将数据库模型序列化为指定模型
            
            models > self.OBJ

            class Model(IDModel):
                OBJ: ProjectObj = ProjectObj ->
                OBJ_DEHYDRATE = async def ....
        """
        cls = self.__class__

        if not models:
            # noinspection PyTypeChecker
            models = self.OBJ or pydantic_model_creator(cls, name=cls.__name__)

        # noinspection PyProtectedMember
        obj = models._enforce_dict_if_root(self)
        if not isinstance(obj, dict):
            try:
                obj = dict(obj)
                for attr_name, formatter in self.AWAIT_OBJ.items():
                    attr = getattr(self, attr_name, None)
                    if attr:
                        attr = await attr
                    if isinstance(formatter, tuple):
                        _attr_name, default = formatter
                    else:
                        _attr_name, default = formatter, None
                    # 不存在默认值的对象会抛出异常
                    if not hasattr(attr, _attr_name) and not isinstance(formatter, tuple):
                        raise ValueError()
                    obj[attr_name] = getattr(attr, _attr_name, default)
            except (TypeError, ValueError) as e:
                exc = TypeError(f'{models.__name__} expected dict not {obj.__class__.__name__}')
                raise ValidationError([ErrorWrapper(exc, loc=ROOT_KEY)], models) from e
        return models(**obj)

    @classmethod
    def last(
            cls: typing.Type['typing_extensions.Self'], using_db: typing.Optional[BaseDBAsyncClient] = None
    ) -> QuerySetSingle[typing.Optional['typing_extensions.Self']:]:
        db = using_db or cls._choose_db()
        return cls._meta.manager.get_queryset().order_by('-id').using_db(db).first()

    @classmethod
    async def from_obj(cls: 'Model', obj=None, **kwargs):
        """ 通过接口模型写入数据库  """
        obj_data = obj.dict() if isinstance(obj, BaseModel) else {}
        obj_data.update(kwargs)
        return await cls.create(**obj_data)


class TimestampMixin:
    created_at: datetime = fields.DatetimeField(auto_now_add=True, description='创建时间')
    updated_at: datetime = fields.DatetimeField(auto_now=True, description='更新时间')


class IDModel(Model, TimestampMixin, PydanticMixin):
    id = fields.IntField(pk=True, description='id')

    class Meta:
        abstract = True


class UUIDModel(Model, TimestampMixin, PydanticMixin):
    id = fields.UUIDField(pk=True, description='uuid')

    class Meta:
        abstract = True
