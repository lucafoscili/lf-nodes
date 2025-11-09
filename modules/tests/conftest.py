"""Ensure 'modules' package is importable when running pytest from repo root.

We append the lf-nodes root so that 'modules' resolves to
custom_nodes/lf-nodes/modules during test collection.
"""

import os
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
LF_NODES_ROOT = THIS_DIR.parent.parent  # .../custom_nodes/lf-nodes

if str(LF_NODES_ROOT) not in sys.path:
    sys.path.insert(0, str(LF_NODES_ROOT))
