"""Adapters package for external/backing services (storage, external APIs)."""

from .storage_adapter import StorageAdapter, LocalFileStorageAdapter

__all__ = ["StorageAdapter", "LocalFileStorageAdapter"]
