import sys
import os
import logging

import pytest

# ── Ensure wrappers are importable ───────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from test_runner.healing_reporter import HealingReporter

# ── Configure root logger ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)


# ── Register plugin ───────────────────────────────────────────────────────────
def pytest_configure(config):
    config.pluginmanager.register(HealingReporter(), "healing_reporter")


# ── Shared fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def mcp_server_url() -> str:
    return os.getenv("MCP_SERVER_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def demo_app_url() -> str:
    return os.getenv("DEMO_APP_URL", "http://localhost:3000")
