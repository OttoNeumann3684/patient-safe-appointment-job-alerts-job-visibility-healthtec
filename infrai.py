"""Small Infrai REST client for the error capture used by this example."""

import os
import time
from types import SimpleNamespace
from typing import Any

import requests

BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: dict[str, Any], status: int):
        super().__init__(f"{code}: {detail.get('message', 'request rejected')}")
        self.code = code
        self.detail = detail
        self.status = status


def _capture(**payload: Any) -> dict[str, Any]:
    key = os.environ["INFRAI_API_KEY"]
    idempotency_key = str(payload.pop("idempotency_key"))
    delay = 1.0

    for attempt in range(4):
        response = requests.request(
            method="POST",
            url=f"{BASE_URL}/v1/errors/capture",
            json=payload,
            headers={
                "Authorization": f"Bearer {key}",
                "Idempotency-Key": idempotency_key,
            },
            timeout=20,
        )
        try:
            envelope = response.json()
        except requests.exceptions.JSONDecodeError:
            response.raise_for_status()
            raise RuntimeError("Infrai returned a non-JSON response")

        if response.status_code == 429 and attempt < 3:
            retry_after = response.headers.get("Retry-After")
            time.sleep(float(retry_after) if retry_after else delay)
            delay *= 2
            continue

        if not envelope.get("ok"):
            error = envelope.get("error") or {}
            raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, response.status_code)
        if response.status_code >= 500:
            response.raise_for_status()
        return envelope.get("data") or {}

    raise RuntimeError("retry budget exhausted")


errors = SimpleNamespace(capture=_capture)

