from pydantic import BaseModel, Field, field_validator
from enum import Enum


class StatusEnum(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskBase(BaseModel):
    name: str = Field(..., description="Название задачи")
    status: StatusEnum = Field(..., description="Статус задачи")

    @field_validator("name")
    @classmethod
    def name_no_only_dots_or_spaces(cls, v: str) -> str:
        if not any(ch.isalnum() for ch in v) or v.isdigit():
            raise ValueError("Название должно быть непустым и состоять не только из цифр.")
        return v


class Task(TaskBase):
    id: int = Field(..., ge=1, description="Идентификатор задачи")
