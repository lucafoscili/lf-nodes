"""
Models package for workflow_runner.

Keep simple schemas/dataclasses here. We avoid heavy runtime deps; use
dataclasses or pydantic if already present in the repo. Start with a tiny
schemas module.
"""

from .schemas import StartWorkflowSchema

__all__ = ["StartWorkflowSchema"]