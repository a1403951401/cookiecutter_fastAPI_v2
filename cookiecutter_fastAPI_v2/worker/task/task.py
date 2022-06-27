from loguru import logger

from cookiecutter_fastAPI_v2.utils.arq import Worker, CTX


@Worker.task
async def async_message(ctx: CTX, msg: str):
    logger.debug("async_message")
    return f'async_message: {msg}'
