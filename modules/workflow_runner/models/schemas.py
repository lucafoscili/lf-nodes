from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# region Workflow start
@dataclass
class StartWorkflowSchema:
    name: str
    params: Dict[str, Any] = field(default_factory=dict)
    user: Optional[str] = None
    run_async: bool = True

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]) -> 'StartWorkflowSchema':
        if not isinstance(obj, dict):
            raise TypeError("StartWorkflowSchema requires a dict")
        return cls(
            name=obj.get('name', ''),
            params=obj.get('params', {}),
            user=obj.get('user'),
            run_async=obj.get('run_async', True),
        )
# endregion