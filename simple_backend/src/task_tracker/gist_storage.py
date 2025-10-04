import os
import json
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from llm_client import LLMClient

load_dotenv()


class GistTaskStorage:
    def __init__(self):
        self.gist_id = os.getenv("GIST_ID")
        self.token = os.getenv("GIST_TOKEN")
        self.filename = os.getenv("FILENAME", "tasks.json")
        self.user_agent = os.getenv("USER_AGENT", "task-tracker")
        self.base_url = f"https://api.github.com/gists/{self.gist_id}"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": self.user_agent,
        }
        self.llm = LLMClient()

    def _load(self) -> List[Dict[str, Any]]:
        r = requests.get(self.base_url, headers=self.headers)
        data = r.json()
        content = data["files"][self.filename]["content"]
        return json.loads(content)

    def _dump(self, tasks: List[Dict[str, Any]]) -> None:
        payload = {
            "files": {
                self.filename: {
                    "content": json.dumps(tasks, ensure_ascii=False, indent=2)
                }
            }
        }
        requests.patch(self.base_url, headers=self.headers, json=payload)

    def _inject_solution_into_name(self, name: str, solution: Optional[str]) -> str:
        if solution:
            return f"{name} Решение от нейросети: {solution}"
        return name

    def list(self) -> List[Dict[str, Any]]:
        return self._load()

    def create(self, task: Dict[str, Any]) -> Dict[str, Any]:
        tasks = self._load()
        new_id = max([t.get("id", 0) for t in tasks], default=0) + 1
        task["id"] = new_id
        base_text = task["name"]
        solution = self.llm.solve_for_task_text(base_text)
        task["name"] = self._inject_solution_into_name(base_text, solution)
        tasks.append(task)
        self._dump(tasks)
        return task

    def update(self, task_id: int, updated: Dict[str, Any]) -> Dict[str, Any]:
        tasks = self._load()
        for t in tasks:
            if t["id"] == task_id:
                base_text = updated["name"]
                solution = self.llm.solve_for_task_text(base_text)
                updated["name"] = self._inject_solution_into_name(base_text, solution)
                t.update(updated)
                self._dump(tasks)
                return t
        raise KeyError("Task not found")

    def delete(self, task_id: int) -> None:
        tasks = self._load()
        new_tasks = [t for t in tasks if t["id"] != task_id]
        self._dump(new_tasks)
        if len(new_tasks) == len(tasks):
            raise KeyError("Task not found")
        self._dump(new_tasks)
