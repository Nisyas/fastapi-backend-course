import os
import requests
from loguru import logger

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

    def solve_for_task_text(self, task_text: str) -> str | None:
        prompt = (
            "Ты — помощник по выполнению задач. Дай краткий, практичный план решения "
            "и перечисли 3–7 конкретных шагов. Если нужно — добавь советы.\n\n"
            f"Текст задачи:\n{task_text}"
        )
        data = {"model": self.model, "input": prompt}
        logger.debug(f"Отправка запроса к LLM для задачи: {task_text}")
        try:
            resp = requests.post(
                self.base_url, headers=self.headers, json=data, timeout=60
            )

            resp.raise_for_status()
            answer = resp.json()
            text = None

            try:
                text = answer["output"][1]["content"][0]["text"]
            except (KeyError, IndexError, TypeError):
                logger.warning(f"Неожиданный формат ответа от LLM: {answer}")
            if text:
                logger.success("Ответ от LLM успешно получен.")
            else:
                logger.error("Ответ от LLM пустой или некорректный.")
            return text
        
        except requests.exceptions.Timeout:
            logger.error("Таймаут при обращении к LLM (60 секунд).")
        except requests.exceptions.RequestException as e:
            logger.exception(f"Ошибка HTTP при обращении к LLM: {e}")
        except Exception as e:
            logger.exception(f"Неизвестная ошибка при работе с LLM: {e}")
        
        return None