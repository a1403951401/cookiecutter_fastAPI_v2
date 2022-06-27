from cookiecutter_fastAPI_v2.utils import BaseModel


class UserObj(BaseModel):
    username: str
    is_admin: bool = False
    permission: set = set()

