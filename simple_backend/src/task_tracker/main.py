from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

app = FastAPI()
tasks = []
next_id = 1

class AddTask(BaseModel):
    name: str
    status: str

@app.get("/tasks")
def get_tasks():
    return tasks

@app.post("/tasks")
def create_task(task: Annotated[AddTask, Depends()]):
    global next_id
    task["id"] = next_id
    next_id += 1
    tasks.append(task)
    return task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Annotated[AddTask, Depends()]):
    for task in tasks:
        if task["id"] == task_id:
            task.update(updated_task)   # обновляем поля
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return {"ok": True}
    raise HTTPException(status_code=404, detail="Task not found")
