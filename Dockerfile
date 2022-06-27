FROM python:3.10-bullseye

MAINTAINER 1403951401@qq.com

COPY ./ /app

WORKDIR /app

RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip poetry && \
    poetry config virtualenvs.create false && \
    poetry install $(test "${NO_DEV}" && echo "--no-dev") --no-root

CMD ["/bin/bash", "-c", "uvicorn cookiecutter_fastAPI_v2.core.rule:app --host 0.0.0.0 --port 8080 --workers 4"]