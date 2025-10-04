import os
import requests
from typing import Optional

class LLMClient:
    
    def __init__(self) -> None:
        self.account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        self.auth_token = os.environ.get("CLOUDFLARE_AUTH_TOKEN")
        self.model = os.environ.get("CLOUDFLARE_MODEL", "@cf/openai/gpt-oss-20b")
        self.base_url = (
            f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/v1/responses"
        )
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
        }

    def solve_for_task_text(self, task_text: str) -> Optional[str]:
    
        prompt = (
            "Ты — помощник по выполнению задач. Дай краткий, практичный план решения "
            "и перечисли 3–7 конкретных шагов. Если нужно — добавь советы.\n\n"
            f"Текст задачи:\n{task_text}"
        )

        data = {"model": self.model, "input": prompt}

        try:
            resp = requests.post(
                self.base_url, headers=self.headers, json=data, timeout=60
            )

            answer = resp.json()
            return answer["output"][1]["content"][0]["text"]
        except Exception as e:
            print(f"[LLM] Ошибка запроса: {e}")
            return None