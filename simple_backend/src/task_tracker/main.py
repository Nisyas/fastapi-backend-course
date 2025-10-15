from fastapi import (
    FastAPI,
    HTTPException,
    Response,
    status,
    Depends,
)
from typing import Annotated
from gist_storage import GistTaskStorage
from loguru import logger
from logging_setup import setup_logging
from models import Task, TaskBase
from llm_client import LLMClient


setup_logging()
llm = LLMClient()
app = FastAPI(title="📜 Task Tracker with LLM 📜")
tasks = GistTaskStorage(solver=llm.solve_for_task_text)


def to_dict(model: Task) -> dict:
    return model.model_dump()


@app.get("/tasks", response_model=list[Task], status_code=status.HTTP_200_OK)
def get_tasks():
    logger.info("GET /tasks")
    return tasks.list()


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: Annotated[TaskBase, Depends()]):
    logger.info(f"POST /tasks: {task}")
    return tasks.create(to_dict(task))


@app.put("/tasks/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
def update_task(task_id: int, updated_task: Annotated[TaskBase, Depends()]):
    logger.info(f"PUT /tasks/{task_id}")
    try:
        return tasks.update(task_id, to_dict(updated_task))
    except KeyError:
        logger.warning(f"Задача {task_id} не найдена при обновлении")
        raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    logger.info(f"DELETE /tasks/{task_id}")
    try:
        tasks.delete(task_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except KeyError:
        logger.warning(f"Задача {task_id} не найдена при удалении")
        raise HTTPException(status_code=404, detail="Task not found")
