from datetime import datetime

from arq.jobs import Job, JobStatus

from cookiecutter_fastAPI_v2.core.base.app import BaseResponse
from cookiecutter_fastAPI_v2.core.base.router import task_router
from cookiecutter_fastAPI_v2.utils import BaseModel
from cookiecutter_fastAPI_v2.utils.context import context


class Task(BaseModel):
    task: str
    data: dict = None


class TaskResponse(BaseModel):
    task_id: str
    status: JobStatus | None = None
    enqueue_time: datetime | None = None
    start_time: datetime | None = None
    finish_time: datetime | None = None
    result: dict = None

    @classmethod
    async def init(cls, task_id: str) -> 'BaseResponse[TaskResponse]':
        job = Job(job_id=task_id, redis=context.pool)
        info = await job.result_info()
        response = TaskResponse(task_id=task_id, status=await job.status())
        if info:
            response.task = info.function
            response.data = info.kwargs
            response.enqueue_time = info.enqueue_time
            response.start_time = info.start_time
            response.finish_time = info.finish_time
            if not isinstance(info.result, dict):
                info.result = {'result': info.result}
            response.result = info.result
        return BaseResponse(data=response)


@task_router.post("/",
                  summary="创建任务",
                  response_model=BaseResponse[TaskResponse])
async def task(task: Task) -> BaseResponse[TaskResponse]:
    """ http://127.0.0.1:8000/task?message=123 """
    job: Job = await context.pool.enqueue_job(task.task, **task.data)
    return await TaskResponse.init(job.job_id)


@task_router.get("/{task_id}",
                 summary="查询任务",
                 response_model=BaseResponse[TaskResponse])
async def get_task(task_id: str) -> BaseResponse[TaskResponse]:
    return await TaskResponse.init(task_id)
