import typing

CBV_API_ROUTE = '__api_route__'

META_DEFAULT = '__meta_default__'
META_ANNOTATION = '__meta_annotation__'
META_RETURN_TYPE = '__meta_return_type__'
META_FIELDS = '__meta_fields__'
META_AUTO_MODEL = '__meta_auto_model__'

QUERYSET_AUTO_MODEL = '__queryset_auto_model__'
QUERYSET_AUTO_MODEL_READONLY = '__queryset_auto_model_readonly__'

METHOD_FUNCTIONS = {
    '_post_list': 'POST',
    '_delete': 'DELETE',
    '_delete_list': 'DELETE',
    '_put': 'PUT',
    '_put_list': 'PUT',
    '_get': 'GET',
    '_get_list': 'GET',
}

ID_PATH = ['_delete', '_put', '_get']

LIMIT = 20
OFFSET = 0
