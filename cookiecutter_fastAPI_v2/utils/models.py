from pydantic import BaseModel as Model

from cookiecutter_fastAPI_v2.utils.json import loads, dumps, DEFAULT_ENCODERS_BY_TYPE

DEFAULT_ENCODERS_BY_TYPE[Model] = lambda obj: obj.dict()


class BaseModel(Model):
    class Config:
        json_loads = loads
        json_dumps = dumps
        extra = 'allow'
