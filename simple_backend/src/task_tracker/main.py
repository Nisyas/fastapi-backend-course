from typing import Annotated
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
)  # Annotation и Depends для удобного ввода данных
from pydantic import BaseModel  # Pydntic для валидации данных
from gist_storage import GistTaskStorage

app = FastAPI()
tasks = GistTaskStorage()


class AddTask(BaseModel):
    name: str
    status: str


def to_dict(model: BaseModel) -> dict:  # Преобразование pydantic модели в словарь
    return model.model_dump()


@app.get("/tasks")
def get_tasks():
    return tasks.list()


@app.post("/tasks")
def create_task(task: Annotated[AddTask, Depends()]):
    return tasks.create(to_dict(task))


@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Annotated[AddTask, Depends()]):
    try:
        return tasks.update(task_id, to_dict(updated_task))
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    try:
        tasks.delete(task_id)
        return {"ok": True}
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")
