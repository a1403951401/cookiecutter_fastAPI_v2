from datetime import datetime
from typing import Type, Optional

from tortoise import fields, Model, BaseDBAsyncClient, Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel
from tortoise.queryset import QuerySetSingle
import typing_extensions

class PydanticMixin:
    """ 将 Model 序列化为 Pydantic 模型 """
    id: fields.IntField | fields.UUIDField
    OBJ: Type['PydanticModel'] = PydanticModel()

    @classmethod
    def models(cls: Type['typing_extensions.Self']) -> OBJ:
        if cls.OBJ:
            return cls.OBJ
        return pydantic_model_creator(cls, name=cls.__name__)

    @property
    def _pydantic(self) -> Type['PydanticModel']:
        return self.models()

    @property
    def object(self) -> 'OBJ':
        return self._pydantic.parse_obj(self)

    @classmethod
    def last(
            cls: Type['typing_extensions.Self'], using_db: Optional[BaseDBAsyncClient] = None
    ) -> QuerySetSingle[Optional['typing_extensions.Self']:]:
        db = using_db or cls._choose_db()
        return cls._meta.manager.get_queryset().order_by('-id').using_db(db).first()


class TimestampMixin:
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)


class IDModel(Model, TimestampMixin, PydanticMixin):
    id = fields.IntField(pk=True)

    class Meta:
        abstract = True


class UUIDModel(Model, TimestampMixin, PydanticMixin):
    id = fields.UUIDField(pk=True)

    class Meta:
        abstract = True
