import inspect

from fastapi import Depends, APIRouter
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel
from tortoise.queryset import QuerySet

from .model import BaseObjectResponse, BaseListResponse, MetaResponse, ListResponseData
from .wrapper import *


class CBVMeta:
    router: APIRouter = None
    resource_name: str = '/'
    allowed_methods: List[str] = ['POST', 'DELETE', 'PUT', 'GET']
    # 模型
    queryset: QuerySet = None
    # 序列化类型
    base_id_type = int
    base_obj_response = BaseObjectResponse
    base_meta_response = MetaResponse
    base_list_data_response = ListResponseData
    base_list_response = BaseListResponse
    # 查询配置
    fields: Dict[str, TypeVar] = {}
    order_by: List[str] = []
    limit = LIMIT
    offset = OFFSET


def _get_attr(mcs, key):
    meta: CBVMeta = getattr(mcs, 'Meta', None)
    return getattr(meta if hasattr(meta, key) else CBVMeta, key)


class CBVMetaClass(type):
    def __new__(mcs, name, bases, attrs):
        mcs = type.__new__(mcs, name, bases, attrs)
        # 基类不进行序列化
        if not bases:
            return mcs
        # TODO(Martin): 此处需要通过 queryset 生产 auto model 对象用于 post / put
        # 构造 auto 模型
        queryset = _get_attr(mcs, 'queryset')
        if queryset:
            model = pydantic_model_creator(queryset, name=queryset.__name__)
        signature = inspect.signature(mcs.__init__)
        # 构造 __init__ 过滤 self *args **kwargs
        parameters = [
            parameter
            for parameter in list(signature.parameters.values())[1:]
            if parameter.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        ]
        # 构造请求依赖
        parameters.extend([
            inspect.Parameter(
                name=name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation=hint,
                default=getattr(mcs, name, ...))
            for name, hint in get_type_hints(mcs).items()
        ])
        mcs.__signature__ = signature.replace(parameters=parameters)
        # 获取 allowed_methods 对应的路由进行注册
        functions = {}
        for method in _get_attr(mcs, 'allowed_methods'):
            method = method.upper()
            for coroutine_function_name in METHOD_FUNCTIONS:
                if METHOD_FUNCTIONS[coroutine_function_name] == method:
                    functions[coroutine_function_name] = method

        base_obj_response = _get_attr(mcs, 'base_obj_response')
        base_list_response = _get_attr(mcs, 'base_list_response')
        base_path = _get_attr(mcs, 'resource_name')
        # 添加 routers
        router = _get_attr(mcs, 'router')
        for name, coroutine_function in inspect.getmembers(mcs, inspect.iscoroutinefunction):
            # 所有依赖过滤 self
            signature = inspect.signature(coroutine_function)
            parameters = list(signature.parameters.values())
            new_parameters = [parameters[0].replace(default=Depends(mcs))]
            # 通过 fields 获取动态变量
            if getattr(coroutine_function, META_FIELDS, False):
                for field, annotation in _get_attr(mcs, 'fields').items():
                    new_parameters.append(
                        inspect.Parameter(
                            name=field,
                            kind=inspect.Parameter.KEYWORD_ONLY,
                            annotation=annotation,
                            default=None))
            else:
                meta_default = getattr(coroutine_function, META_DEFAULT, {})
                meta_annotation = getattr(coroutine_function, META_ANNOTATION, {})
                for parameter in parameters[1:]:
                    parameter = parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY)
                    if parameter.name in meta_default:
                        parameter = parameter.replace(default=_get_attr(mcs, meta_default[parameter.name]))
                    if parameter.name in meta_annotation:
                        parameter = parameter.replace(annotation=_get_attr(mcs, meta_annotation[parameter.name]))
                    new_parameters.append(parameter)
            signature = signature.replace(parameters=new_parameters)
            coroutine_function.__signature__ = signature
            if name in functions:
                # 获取 api_route 参数
                view_function = getattr(mcs, name[1:], None)
                kwargs = None
                if view_function:
                    kwargs = getattr(view_function, CBV_API_ROUTE, None)
                if not kwargs:
                    if not hasattr(coroutine_function, CBV_API_ROUTE):
                        coroutine_function = api_route()(coroutine_function)
                    kwargs = getattr(coroutine_function, CBV_API_ROUTE)
                # 请求类型
                kwargs['methods'] = [functions[name]]
                # 请求路径
                if not kwargs['path']:
                    kwargs['path'] = base_path
                    if name in ID_PATH:
                        if kwargs['path'][-1] != '/':
                            kwargs['path'] += "/"
                        kwargs['path'] += "{id}"
                # 请求返回值
                if name in METHOD_FUNCTIONS and not kwargs['response_model']:
                    function = getattr(getattr(mcs, name[1:], None), '__annotations__', {}).get('return')
                    dehydrate = getattr(getattr(mcs, 'dehydrate', None), '__annotations__', {}).get('return')
                    if function or dehydrate:
                        kwargs['response_model'] = function or dehydrate
                # 返回值模型序列化
                if kwargs['response_model']:
                    if 'list' in name:
                        if base_list_response and not isinstance(kwargs['response_model'], base_list_response):
                            kwargs['response_model'] = base_list_response[kwargs['response_model']]
                    else:
                        if base_obj_response and not isinstance(kwargs['response_model'], base_obj_response):
                            kwargs['response_model'] = base_obj_response[kwargs['response_model']]
                router.api_route(**kwargs)(coroutine_function)

        # 初始化路由函数
        inspect.getmembers(mcs, inspect.iscoroutinefunction)
        return mcs