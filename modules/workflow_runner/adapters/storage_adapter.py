"""Storage adapter abstraction for workflow_runner.

Provide a simple interface and a local filesystem implementation. The real
project already has its own storage and persistence helpers; this adapter
is a small scaffold to make moving code safer and easier.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path


class StorageAdapter(ABC):
    @abstractmethod
    def save(self, key: str, data: Any) -> None:
        pass

    @abstractmethod
    def load(self, key: str) -> Optional[Any]:
        pass


class LocalFileStorageAdapter(StorageAdapter):
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: Any) -> None:
        p = self.root / key
        p.write_text(str(data), encoding="utf-8")

    def load(self, key: str) -> Optional[str]:
        p = self.root / key
        if not p.exists():
            return None
        return p.read_text(encoding="utf-8")
