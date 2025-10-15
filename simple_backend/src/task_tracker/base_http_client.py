from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urljoin
import requests
from loguru import logger


class BaseHTTPClient(ABC):
    timeout: float = 60.0

    @property
    @abstractmethod
    def base_url(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def default_headers(self) -> dict[str, str]:
        raise NotImplementedError

    def _make_url(self, path: str | None = None) -> str:
        return (
            self.base_url
            if not path
            else urljoin(self.base_url.rstrip("/") + "/", path.lstrip("/"))
        )

    def _merge_headers(self, extra: dict[str, str] | None) -> dict[str, str]:
        if not extra:
            return dict(self.default_headers)
        h = dict(self.default_headers)
        h.update(extra)
        return h

    def get(
        self,
        path: None | str = None,
        *,
        params: None | dict[str, Any] = None,
        headers: None | dict[str, str] = None,
    ) -> requests.Response:
        url = self._make_url(path)
        hdrs = self._merge_headers(headers)
        logger.debug(f"GET {url} params={params}")
        resp = requests.get(url, params=params, headers=hdrs, timeout=self.timeout)
        logger.debug(f"GET {url} -> {resp.status_code}")
        return resp

    def post(
        self,
        path: None | str = None,
        *,
        json: Any = None,
        data: Any = None,
        headers: None | dict[str, str] = None,
    ) -> requests.Response:
        url = self._make_url(path)
        hdrs = self._merge_headers(headers)
        logger.debug(f"POST {url} json={bool(json)} data={bool(data)}")
        resp = requests.post(
            url, json=json, data=data, headers=hdrs, timeout=self.timeout
        )
        logger.debug(f"POST {url} -> {resp.status_code}")
        return resp

    def patch(
        self,
        path: None | str = None,
        *,
        json: Any = None,
        data: Any = None,
        headers: None | dict[str, str] = None,
    ) -> requests.Response:
        url = self._make_url(path)
        hdrs = self._merge_headers(headers)
        logger.debug(f"PATCH {url} json={bool(json)} data={bool(data)}")
        resp = requests.patch(
            url, json=json, data=data, headers=hdrs, timeout=self.timeout
        )
        logger.debug(f"PATCH {url} -> {resp.status_code}")
        return resp
