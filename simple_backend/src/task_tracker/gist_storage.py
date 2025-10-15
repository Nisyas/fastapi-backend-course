import os
import json
from typing import Any, Callable
from dotenv import load_dotenv
from loguru import logger
from base_http_client import BaseHTTPClient
from models import Task
from pydantic import TypeAdapter

load_dotenv()
TasksAdapter = TypeAdapter(list[Task])

class GistTaskStorage(BaseHTTPClient):
    def __init__(self, solver: Callable[[str], str | None] | None = None):
        self.gist_id = os.getenv("GIST_ID")
        self.token = os.getenv("GIST_TOKEN")
        self.filename = os.getenv("FILENAME", "tasks.json")
        self.user_agent = os.getenv("USER_AGENT", "task-tracker")
        self._solver = solver

    @property
    def base_url(self) -> str:
        return f"https://api.github.com/gists/{self.gist_id}"

    @property
    def default_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": self.user_agent,
        }

    def _load(self) -> list[Task]:
        resp = self.get()
        try:
            resp.raise_for_status()
        except Exception as e:
            logger.exception(f"Ошибка загрузки Gist: {e}")
            raise RuntimeError("Не удалось загрузить Gist") from e

        try:
            data = resp.json()
            content = data["files"][self.filename]["content"]
            raw_tasks = json.loads(content)
            tasks = [Task.model_validate(t) for t in raw_tasks]
            logger.success("Задачи загружены из Gist")
            return tasks
        except Exception as e:
            logger.exception(f"Некорректный формат данных Gist: {e}")
            raise RuntimeError("Некорректные данные Gist") from e

    def _dump(self, tasks: list[dict[str, Any]]) -> None:
        payload = {
            "files": {
                self.filename: {
                    "content": TasksAdapter.dump_json(tasks, indent=2).decode("utf-8")
                }
            }
        }
        resp = self.patch(json=payload)
        if resp.status_code != 200:
            logger.error(
                f"Ошибка сохранения Gist: {resp.status_code} {resp.text[:200]}"
            )
        else:
            logger.success("Изменения сохранены в Gist")

    @staticmethod
    def _inject_solution(name: str, solution: None | str) -> str:
        return f"{name} Решение от нейросети: {solution}" if solution else name

    def list(self) -> list[Task]:
        logger.info("Получение списка задач")
        return self._load()

    def create(self, task: dict[str, Any]) -> Task:
        logger.info(f"Создание задачи: {task}")
        tasks = self._load()

        new_id = max((t.id for t in tasks), default=0) + 1

        task = Task(id=new_id, **task)

        base_text = task.name
        if self._solver:
            solution = self._solver(base_text)
            task.name = self._inject_solution(base_text, solution)

        tasks.append(task)
        self._dump(tasks)
        logger.success(f"Задача создана: id={task.id}")
        return task

    def update(self, task_id: int, updated: dict[str, Any]) -> Task:
        logger.info(f"Обновление задачи id={task_id}")
        tasks = self._load()
        for i, t in enumerate(tasks):
            if t.id == task_id:
                updated_task = t.model_copy(update=updated)
                base_text = updated_task.name
                if self._solver:
                    solution = self._solver(base_text)
                    updated_task.name = self._inject_solution(base_text, solution)

                tasks[i] = updated_task
                self._dump(tasks)
                logger.success(f"Задача {task_id} обновлена")
                return updated_task
        logger.warning(f"Задача {task_id} не найдена для обновления")
        raise KeyError("Task not found")

    def delete(self, task_id: int) -> None:
        logger.warning(f"Удаление задачи id={task_id}")
        tasks = self._load()
        for i, t in enumerate(tasks):
            if t.id == task_id:
                del tasks[i]
                self._dump(tasks)
                logger.success(f"Задача {task_id} удалена")
                return
        logger.error(f"Задача {task_id} не найдена при удалении")
        raise KeyError("Task not found")
