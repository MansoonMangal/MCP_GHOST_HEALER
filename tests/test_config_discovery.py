"""Tests for ghost.yaml discovery and cache path anchoring."""
import os
from pathlib import Path

import pytest

from ghost_healer.core import config as config_module
from ghost_healer.core.config import find_ghost_yaml, load_config, resolve_config_path
from ghost_healer.core.cache import HealingCache


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_find_ghost_yaml_from_subdirectory():
    sub = REPO_ROOT / "demo" / "playwright-python"
    if not sub.is_dir():
        pytest.skip("demo/playwright-python not present")
    found = find_ghost_yaml(str(sub))
    assert found is not None
    assert Path(found).name == "ghost.yaml"
    assert Path(found).resolve().parent == REPO_ROOT.resolve()


def test_resolve_config_path_sets_config_dir_to_repo_root():
    sub = REPO_ROOT / "demo" / "playwright-python"
    if not sub.is_dir():
        pytest.skip("demo/playwright-python not present")
    orig = os.getcwd()
    try:
        os.chdir(sub)
        yaml_path, config_dir = resolve_config_path()
        assert yaml_path is not None
        assert Path(config_dir).resolve() == REPO_ROOT.resolve()
    finally:
        os.chdir(orig)


def test_cache_path_anchored_to_config_dir(monkeypatch):
    sub = REPO_ROOT / "demo" / "playwright-python"
    if not sub.is_dir():
        pytest.skip("demo/playwright-python not present")
    monkeypatch.chdir(sub)
    cfg = load_config()
    assert Path(cfg.config_dir).resolve() == REPO_ROOT.resolve()
    expected_db = os.path.join(cfg.config_dir, ".ghost_cache.db")
    cache = HealingCache(db_path=expected_db)
    assert Path(cache.db_path).resolve().parent == REPO_ROOT.resolve()
    assert Path(cache.db_path).name == ".ghost_cache.db"


def test_reload_config_module_finds_yaml(monkeypatch):
    sub = REPO_ROOT / "demo" / "playwright-python"
    if not sub.is_dir():
        pytest.skip("demo/playwright-python not present")
    monkeypatch.chdir(sub)
    reloaded = config_module.load_config()
    assert reloaded.mcp_server.confidence_threshold == 0.5
    assert Path(reloaded.config_dir).resolve() == REPO_ROOT.resolve()
