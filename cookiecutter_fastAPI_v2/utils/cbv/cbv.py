from fastapi import Depends
from pydantic.main import ModelMetaclass
from starlette.exceptions import HTTPException
from tortoise import Model
from tortoise.contrib.pydantic import PydanticModel
from tortoise.exceptions import DoesNotExist
from tortoise.queryset import QuerySet

from .base import CBVMetaClass, CBVMeta
from .wrapper import *


class CBV(metaclass=CBVMetaClass):
    """ FastAPI 类路由的实现

    """
    Meta = CBVMeta

    def get_meta(self, key, default=None):
        return getattr(self.Meta, key, getattr(CBVMeta, key, default))

    @property
    def queryset(self):
        """ 同时返回关联的外键内容 """
        queryset = self.Meta.queryset
        if not isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset.prefetch_related(*list(queryset.model._meta.fetch_fields))

    @property
    def model(self):
        if isinstance(self.queryset, QuerySet):
            return self.queryset.model
        return self.queryset

    @property
    def base_obj_response(self):
        return self.get_meta('base_obj_response')

    @property
    def base_meta_response(self):
        return self.get_meta('base_meta_response')

    @property
    def base_list_data_response(self):
        return self.get_meta('base_list_data_response')

    @property
    def base_list_response(self):
        return self.get_meta('base_list_response')

    @set_meta(META_AUTO_MODEL, value=True)
    async def _post_list(self, data: ModelMetaclass):
        obj = await self.post_list(data)
        return self.base_obj_response(data=await self.dehydrate(obj, for_list=False))

    async def post_list(self, data: ModelMetaclass):
        return await self.model.create(**data.dict())

    @set_meta(META_ANNOTATION, id='base_id_type')
    async def get_obj(self, id) -> Model:
        """ 查询操作对象 """
        try:
            return await self.queryset.get(id=id)
        except DoesNotExist:
            raise HTTPException(status_code=404)

    async def delete(self, obj: Model = Depends(get_obj)):
        raise NotImplementedError

    async def delete_list(self):

        raise NotImplementedError

    async def put(self, obj: Model = Depends(get_obj)):
        raise NotImplementedError

    async def put_list(self):
        raise NotImplementedError

    @set_meta(META_FIELDS, value=True)
    async def apply_filters(self, **kwargs: Dict[str, Any]) -> QuerySet:
        """ 构建query """
        queryset = self.queryset.filter(**{
            key: value for key, value in kwargs.items()
            if value is not None
        })
        # 预加载所有关联外键
        return queryset.prefetch_related(*list(queryset.model._meta.fetch_fields))

    async def apply_sorting(
            self,
            query: QuerySet = Depends(apply_filters)
    ) -> QuerySet:
        """ 构建排序 """
        return query.order_by(*self.get_meta('order_by'))

    async def apply_limit_and_offset(self,
                                     query: QuerySet,
                                     limit: int = None, offset: int = None
                                     ) -> (QuerySet, Meta.base_meta_response):
        """ 构建分页 """
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query, self.base_meta_response(limit=limit, offset=offset, total_count=await query.count())

    async def fetch_related(self, obj: Model):
        describe = obj.describe()
        for key in ['fk_fields', 'backward_fk_fields', 'o2o_fields', 'backward_o2o_fields', 'm2m_fields']:
            await obj.fetch_related(*[field['name'] for field in describe[key]])
            await obj.fetch_related('created_at', 'updated_at')

    async def dehydrate(self, obj: Model, for_list: bool = False):
        """ 序列化数据库模型返回值的方法

        Args:
            obj: 数据库 orm 模型
            for_list: 判断是 get / get_list
        """
        model: Type[PydanticModel] = self.get_meta(QUERYSET_AUTO_MODEL)
        return model.from_orm(obj)

    async def _get(self, obj: Model = Depends(get_obj)):
        obj = await self.get(obj)
        return self.base_obj_response(data=await self.dehydrate(obj, for_list=False))

    async def get(self, obj: Model):
        return obj

    @set_meta(META_DEFAULT, limit='limit', offset='offset')
    async def _get_list(self,
                        query: QuerySet = Depends(apply_filters),
                        limit: int = None, offset: int = None):
        query = await self.get_list(query)
        query = await self.apply_sorting(query)
        query, meta = await self.apply_limit_and_offset(query, limit, offset)

        objects = [
            await self.dehydrate(obj, for_list=True)
            async for obj in query]

        return self.base_list_response(
            data=self.base_list_data_response(meta=meta, objects=objects)
        )

    async def get_list(self, query: QuerySet):
        return query
