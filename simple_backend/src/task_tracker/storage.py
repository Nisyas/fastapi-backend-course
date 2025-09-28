import json
from pathlib import Path
from typing import List, Dict, Any


class FileTaskStorage:
    def __init__(self, path: str = "tasks.json") -> None:
        self.path = Path(path)
        if not self.path.exists():
            self._write([])

    def _read(self) -> List[Dict[str, Any]]:
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: List[Dict[str, Any]]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def list(self) -> List[Dict[str, Any]]:
        return self._read()

    def create(self, task: Dict[str, Any]) -> Dict[str, Any]:
        data = self._read()
        task["id"] = len(data) + 1
        data.append(task)
        self._write(data)
        return task

    def update(self, task_id: int, updated: Dict[str, Any]) -> Dict[str, Any]:
        data = self._read()
        for task in data:
            if task["id"] == task_id:
                task.update(updated)
                self._write(data)
                return task
        raise KeyError("Task not found")

    def delete(self, task_id: int) -> None:
        data = self._read()
        new_data = [t for t in data if t["id"] != task_id]
        if len(new_data) == len(data):
            raise KeyError("Task not found")
        self._write(new_data)
