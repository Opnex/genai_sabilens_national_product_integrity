"""
conftest.py — A4 Fusion Engine
================================
Fixes the ModuleNotFoundError when running tests from any subfolder.

This file is automatically loaded by pytest before any test runs.
It adds the fusion_engine root directory to sys.path so that imports
like `from signals.a1_visual_adapter import adapt` work regardless
of which directory pytest is invoked from.

USAGE (from any location inside the project):
  cd C:\Dev\sabilens\ai_engine\fusion_engine
  pytest                          ← runs all tests
  pytest tests/test_fusion.py     ← runs specific file
  pytest -v                       ← verbose output

DO NOT run tests with `python -m test_fusion` from inside the test/ folder.
Always use pytest from the fusion_engine root.
"""

import sys
import os

# Add the fusion_engine root to sys.path
# This resolves: signals/, core/, config/, utils/ as top-level imports
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)