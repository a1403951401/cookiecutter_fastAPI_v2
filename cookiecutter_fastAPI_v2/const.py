import datetime

TOKEN_MAX_AGE = datetime.timedelta(days=30)

USER_CREATE_CODE = 'user.create'
USER_GET_CODE = 'user.get'
USER_UPDATE_CODE = 'user.update'
USER_UPDATE_ADMIN_CODE = 'user.update.admin'

TOKEN_SOURCE_LOGIN = 'login'

TOKEN_SOURCE = (
    (TOKEN_SOURCE_LOGIN, 'login'),
)
