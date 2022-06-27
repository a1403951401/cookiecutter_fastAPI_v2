import typing

from cookiecutter_fastAPI_v2 import const

PERMISSION_MAP = {}
ALLOW_VIEW_NAMES = {}


class PermissionObj(dict):
    parent: typing.List[str]

    def __init__(self,
                 key,
                 title=None,
                 children: typing.List['PermissionObj'] = None,
                 allow_view_name=False):
        """ 用户权限权限

        Args:
          key: 权限key「唯一」
          title: 前端展示名称
          children: 下级权限
          allow_view_name: 当为 True 时, viwe 视图 allowed_view_names 会包含该key
        """
        if key in PERMISSION_MAP:
            raise ValueError('key %s already existed.', key)
        self.parent = []
        super(PermissionObj, self).__init__({
            'key': key,
        })
        if title:
            self['title'] = title

        if children:
            self.set_parent_and_children(key, children)

        if allow_view_name:
            ALLOW_VIEW_NAMES[key] = self

        PERMISSION_MAP[key] = self

    def set_parent_and_children(self, key, children):
        for c in children:
            c.parent.append(key)
            c.set_parent_and_children(key, c.get('children', []))
        if children:
            self['children'] = children


PERMISSION = PermissionObj('user', '用户管理', [
    PermissionObj(const.USER_GET_CODE, '查询用户'),
    PermissionObj(const.USER_CREATE_CODE, '创建用户'),
    PermissionObj(const.USER_UPDATE_CODE, '修改用户'),
    PermissionObj(const.USER_UPDATE_ADMIN_CODE, '修改用户密码'),
], allow_view_name=True)
