import sys

from loguru import logger

from .json import dumps, loads
from .log import formatter
from .models import BaseModel
from ..config import config

logger.remove()
logger.add(sys.stderr, level='DEBUG' if config.DEBUG else 'INFO', format=formatter)
