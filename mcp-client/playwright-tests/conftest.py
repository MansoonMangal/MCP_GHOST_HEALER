"""
conftest.py for playwright-tests directory.
Provides page-level fixtures and test-local setup.
"""
import sys
import os
import pytest

# Ensure wrappers are importable from test files
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
