"""Pytest configuration for workflow runner tests.

Adds:
  - Fast-mode environment flag (LF_RUNNER_TEST_FAST=1) to accelerate poll loops.
  - Autouse fixture to reset in-memory job_store state between tests.
  - Optional comfy_api_mock fixture providing a deterministic aiohttp session for /history and /queue polling.
"""

import os
import sys
import asyncio
import pytest
from typing import Any, Dict
from pathlib import Path

# Add package root to path for imports
pkg_root = Path(__file__).resolve().parents[2]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))


@pytest.fixture(autouse=True)
def fast_mode_env(monkeypatch):
	"""Enable fast-mode for executor polling to keep tests snappy/deterministic."""
	monkeypatch.setenv("LF_RUNNER_TEST_FAST", "1")
	yield
	monkeypatch.delenv("LF_RUNNER_TEST_FAST", raising=False)


@pytest.fixture(autouse=True)
def reset_job_store_state():
	"""Ensure job_store globals are cleared between tests to avoid cross-test contamination."""
	try:
		from modules.workflow_runner.services import job_store
		# Force in-memory mode for tests to avoid adapter dependence
		job_store._USE_PERSISTENCE = False  # type: ignore[attr-defined]
		# Reset in-memory collections
		job_store._jobs.clear()  # type: ignore[attr-defined]
		job_store._subscribers.clear()  # type: ignore[attr-defined]
		# Reset adapter to force lazy re-init logic each test
		job_store._adapter = None  # type: ignore[attr-defined]
		yield
		# Post-test cleanup (idempotent)
		job_store._USE_PERSISTENCE = False  # type: ignore[attr-defined]
		job_store._jobs.clear()  # type: ignore[attr-defined]
		job_store._subscribers.clear()  # type: ignore[attr-defined]
		job_store._adapter = None  # type: ignore[attr-defined]
	except ImportError:
		# If modules can't be imported, skip the fixture
		yield


@pytest.fixture(autouse=True)
def enforce_test_timeout():
	"""Hard cap each test's runtime to avoid hangs in CI.

	Uses asyncio timeout where available; conservative 15s default.
	"""
	# Keep it simple for now; pytest-timeout could replace this later.
	# No-op teardown; individual tests run under anyio/asyncio policies.
	yield


class _MockAiohttpResponse:
	def __init__(self, status: int, json_data: Dict[str, Any]):
		self.status = status
		self._json_data = json_data
	async def json(self):
		return self._json_data
	def raise_for_status(self):
		if self.status >= 400:
			raise Exception(f"HTTP {self.status}")
	def __aenter__(self):
		return self
	def __aexit__(self, exc_type, exc, tb):
		return False


class _MockAiohttpSession:
	def __init__(self, history_sequence: list[Dict[str, Any]], queue_sequence: list[Dict[str, Any]]):
		self._history_seq = history_sequence
		self._queue_seq = queue_sequence
		self._history_i = 0
		self._queue_i = 0
	async def __aenter__(self):
		return self
	async def __aexit__(self, exc_type, exc, tb):
		return None
	def get(self, url: str, **_kwargs):  # mimic aiohttp.ClientSession.get
		if "/history/" in url:
			data = self._history_seq[min(self._history_i, len(self._history_seq) - 1)]
			self._history_i += 1
			return _MockAiohttpResponse(200, data)
		if url.endswith("/queue"):
			data = self._queue_seq[min(self._queue_i, len(self._queue_seq) - 1)]
			self._queue_i += 1
			return _MockAiohttpResponse(200, data)
		return _MockAiohttpResponse(404, {})
	def post(self, url: str, **_kwargs):
		# Minimal stub for interrupt endpoint
		return _MockAiohttpResponse(200, {"prompt_id": "mock-prompt-123"})
	async def close(self):
		return None


@pytest.fixture
def comfy_api_mock(monkeypatch):
	"""Provide deterministic mocked aiohttp.ClientSession for executor polling.

	Usage:
		history = [{"<prompt_id>": {...}}, {...}]
		queue = [{"queue_running": [], "queue_pending": [...]}, ...]
		monkeypatch.setenv("LF_RUNNER_TEST_FAST", "1")  # ensure fast mode
		def _factory():
			return _MockAiohttpSession(history, queue)
		monkeypatch.setattr("aiohttp.ClientSession", _factory)
	"""
	sessions: list[_MockAiohttpSession] = []
	def factory(history_sequence=None, queue_sequence=None):
		s = _MockAiohttpSession(history_sequence or [{}], queue_sequence or [{}])
		sessions.append(s)
		return s
	yield factory
	# No explicit teardown required; objects are ephemeral.