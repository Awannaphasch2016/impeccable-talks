"""Small synchronous client for Weaver's loopback Gas City bridge."""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Callable

import requests

log = logging.getLogger("weaver")

PHASES = {"discovery", "implementation", "delivery"}
TERMINAL_RUN_STATUSES = {"completed", "rejected", "cancelled", "errored"}


class WeaverError(RuntimeError):
    """A Weaver request failed or returned an unusable response."""


class WeaverClient:
    def __init__(self, base_url: str, api_key: str,
                 session: requests.Session | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def _request(self, method: str, path: str,
                 body: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            response = self.session.request(
                method, self.base_url + path, json=body, timeout=60,
            )
        except requests.RequestException as exc:
            raise WeaverError(f"Weaver {method} {path} failed: {exc}") from exc
        if response.status_code >= 400:
            try:
                detail = response.json().get("error")
            except (ValueError, AttributeError):
                detail = response.text
            raise WeaverError(
                f"Weaver {method} {path}: {response.status_code} {detail or 'request failed'}"
            )
        try:
            result = response.json()
        except ValueError as exc:
            raise WeaverError(f"Weaver {method} {path} returned invalid JSON") from exc
        if not isinstance(result, dict):
            raise WeaverError(f"Weaver {method} {path} returned a non-object response")
        return result

    @staticmethod
    def _app_path(app_id: int, suffix: str) -> str:
        if not isinstance(app_id, int) or isinstance(app_id, bool) or app_id <= 0:
            raise WeaverError("Weaver app id must be a positive integer")
        return f"/v1/apps/{app_id}/{suffix}"

    def link(self, app_id: int, gas_city_project_id: str) -> dict[str, Any]:
        return self._request(
            "PUT", self._app_path(app_id, "link"),
            {"gasCityProjectId": gas_city_project_id},
        )

    def post_message(self, app_id: int, phase: str, idempotency_key: str,
                     role: str, content: str) -> dict[str, Any]:
        if phase not in PHASES:
            raise WeaverError(f"unknown Weaver phase: {phase}")
        return self._request(
            "POST", self._app_path(app_id, f"phases/{phase}/messages"),
            {"idempotencyKey": idempotency_key, "role": role, "content": content},
        )

    def state(self, app_id: int) -> dict[str, Any]:
        return self._request("GET", self._app_path(app_id, "factory-state"))

    def approve_phase(self, app_id: int, phase: str) -> dict[str, Any]:
        if phase not in PHASES:
            raise WeaverError(f"unknown Weaver phase: {phase}")
        return self._request(
            "POST", self._app_path(app_id, f"phases/{phase}/approve"), {},
        )

    def start_run(self, app_id: int, phase: str, idempotency_key: str,
                  prompt: str) -> dict[str, Any]:
        if phase not in PHASES:
            raise WeaverError(f"unknown Weaver phase: {phase}")
        return self._request(
            "POST", self._app_path(app_id, f"phases/{phase}/runs"),
            {"idempotencyKey": idempotency_key, "prompt": prompt},
        )

    def get_run(self, run_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/runs/{run_id}")

    def run_and_wait(self, app_id: int, phase: str, idempotency_key: str,
                     prompt: str, timeout: float = 1800,
                     poll_interval: float = 1,
                     clock: Callable[[], float] = time.monotonic,
                     sleep: Callable[[float], None] = time.sleep) -> dict[str, Any]:
        """Start an idempotent local-agent run and wait for a terminal result."""
        run = self.start_run(app_id, phase, idempotency_key, prompt)
        run_id = run.get("runId")
        if not isinstance(run_id, str) or not run_id:
            raise WeaverError("Weaver run response has no runId")
        deadline = clock() + timeout
        while run.get("status") not in TERMINAL_RUN_STATUSES:
            if clock() >= deadline:
                raise WeaverError(f"Weaver run {run_id} did not finish within {timeout:g}s")
            sleep(poll_interval)
            run = self.get_run(run_id)
        return run


def weaver_from_env() -> WeaverClient | None:
    """Return a configured client, or None when the integration is disabled."""
    base_url = os.getenv("WEAVER_BASE_URL", "").strip()
    api_key = os.getenv("WEAVER_API_KEY", "").strip()
    if not base_url and not api_key:
        log.info("Weaver integration off: WEAVER_BASE_URL and WEAVER_API_KEY are unset")
        return None
    if not base_url or not api_key:
        log.warning(
            "Weaver integration off: %s is unset",
            "WEAVER_BASE_URL" if not base_url else "WEAVER_API_KEY",
        )
        return None
    return WeaverClient(base_url, api_key)
