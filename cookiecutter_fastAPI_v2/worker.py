import os
import pkgutil
import sys
from importlib import import_module

sys.path.append(os.getcwd())

from cookiecutter_fastAPI_v2.utils import *
from cookiecutter_fastAPI_v2.utils.arq import Worker


def import_paths(*module_list: str):
    """ 由于使用递归导入的方法，文件夹须通过 __init__.py 声明该目录为包 """
    for filefiner, name, ispkg in pkgutil.iter_modules([str(config.PROJECT_PATH.joinpath(*module_list))]):
        import_paths(*module_list, name)
        if import_module(".".join([config.PROJECT_NAME, *module_list, name])):
            logger.debug(f"import {'.'.join([config.PROJECT_NAME, *module_list, name])}")


# 载入
for name, path in config.PATH.items():
    logger.debug(f"import {name} models: {config.PROJECT_NAME}.{path.replace('/', '.')}")
    import_paths(*(path.split('/')))

if __name__ == '__main__':
    Worker()
