from loguru import logger

from cookiecutter_fastAPI_v2.utils.arq import Worker, CTX


@Worker.cron(second=1)
async def async_cron(ctx: CTX):
    logger.debug("this is cron job")
