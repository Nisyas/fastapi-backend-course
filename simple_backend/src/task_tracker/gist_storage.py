import os
import json
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

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

    def list(self) -> List[Dict[str, Any]]:
        return self._load()

    def create(self, task: Dict[str, Any]) -> Dict[str, Any]:
        tasks = self._load()
        new_id = max([t.get("id", 0) for t in tasks], default=0) + 1
        task["id"] = new_id
        tasks.append(task)
        self._dump(tasks)
        return task

    def update(self, task_id: int, updated: Dict[str, Any]) -> Dict[str, Any]:
        tasks = self._load()
        for t in tasks:
            if t["id"] == task_id:
                t.update(updated)
                self._dump(tasks)
                return t
        raise KeyError("Task not found")

    def delete(self, task_id: int) -> None:
        tasks = self._load()
        new_tasks = [t for t in tasks if t["id"] != task_id]
        self._dump(new_tasks)
