import datetime

TOKEN_MAX_AGE = datetime.timedelta(days=30)

# 权限
PERMISSION_USER_CREATE_CODE = 'user.create'  # 创建用户
PERMISSION_USER_DELETE_CODE = 'user.delete'  # 删除用户
PERMISSION_USER_UPDATE_CODE = 'user.update'  # 修改用户
PERMISSION_USER_GET_CODE = 'user.get'  # 查询用户

TOKEN_SOURCE_LOGIN = 'login'  # 登录 token
TOKEN_SOURCE_USER = 'user'  # 用户自建 token
TOKEN_SOURCE_PROJECT = 'project'  # 知识库 token

TOKEN_SOURCE = (
    (TOKEN_SOURCE_LOGIN, 'login'),  # 登录 token
    (TOKEN_SOURCE_USER, 'user'),  # 用户自建 token
    (TOKEN_SOURCE_PROJECT, 'project'),  # 用户自建 token
)
