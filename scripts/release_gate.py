"""
Release gate validator for Beta / RC / GA.

Usage:
  python scripts/release_gate.py --stage beta
  python scripts/release_gate.py --stage rc
  python scripts/release_gate.py --stage ga
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: Path | None = None) -> None:
    program = shutil.which(cmd[0]) or shutil.which(f"{cmd[0]}.cmd") or cmd[0]
    completed = subprocess.run([program, *cmd[1:]], cwd=str(cwd or ROOT), check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")


def has_cmd(name: str) -> bool:
    return shutil.which(name) is not None


def require_paths(paths: Iterable[Path]) -> None:
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise RuntimeError("Missing required files:\n- " + "\n- ".join(missing))


def beta_checks(strict_tools: bool) -> None:
    require_paths(
        [
            ROOT / "mcp-server" / "app" / "main.py",
            ROOT / "mcp-server" / "mcp_gateway" / "server.py",
            ROOT / "ghost_healer" / "plugin" / "pytest_ghost.py",
            ROOT / "sdk" / "ts" / "src" / "auto-activate.js",
            ROOT / "docs" / "MIGRATION_MCP_V1.md",
            ROOT / "docs" / "ZERO_CHANGE_INSTALL.md",
        ]
    )

    run([sys.executable, "-m", "pytest", "mcp-server/tests/", "-q"])
    run([sys.executable, "-m", "pytest", "tests/", "-q"])

    # TS package should build for beta scope.
    if has_cmd("npm"):
        dist_dir = ROOT / "sdk" / "ts" / "dist"
        if dist_dir.exists():
            shutil.rmtree(dist_dir, ignore_errors=True)
        run(["npm", "install"], cwd=ROOT / "sdk" / "ts")
        run(["npm", "run", "build"], cwd=ROOT / "sdk" / "ts")
    elif strict_tools:
        raise RuntimeError("npm not found but strict tool checks are enabled")
    else:
        print("[release-gate] skipping TS build (npm not found)")


def rc_checks(strict_tools: bool) -> None:
    beta_checks(strict_tools=strict_tools)
    require_paths(
        [
            ROOT / "ghost_healer" / "framework" / "java" / "GhostHealerAgent.java",
            ROOT
            / "ghost_healer"
            / "framework"
            / "java"
            / "META-INF"
            / "services"
            / "org.junit.jupiter.api.extension.Extension",
            ROOT / "mcp-server" / "middleware" / "auth.py",
            ROOT / "mcp-server" / "middleware" / "payload_limit.py",
            ROOT / "render.yaml",
        ]
    )

    # Java compile smoke check for RC.
    if has_cmd("mvn"):
        run(["mvn", "-f", "demo/pw-java/pom.xml", "-q", "-DskipTests", "compile"])
    elif strict_tools:
        raise RuntimeError("mvn not found but strict tool checks are enabled")
    else:
        print("[release-gate] skipping Java compile (mvn not found)")


def ga_checks(strict_tools: bool) -> None:
    rc_checks(strict_tools=strict_tools)
    require_paths([ROOT / ".github" / "workflows" / "test.yml"])

    # GA should at least lint core code in addition to tests/build smoke.
    run([sys.executable, "-m", "pip", "install", "flake8"])
    run(
        [
            sys.executable,
            "-m",
            "flake8",
            "mcp-server/controllers/",
            "mcp-server/mcp_gateway/",
            "mcp-server/middleware/",
            "scripts/release_gate.py",
            "scripts/verify_slo.py",
            "--max-line-length=120",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["beta", "rc", "ga"], required=True)
    parser.add_argument(
        "--strict-tools",
        action="store_true",
        help="fail if npm/mvn tools are missing",
    )
    args = parser.parse_args()

    if args.stage == "beta":
        beta_checks(strict_tools=args.strict_tools)
    elif args.stage == "rc":
        rc_checks(strict_tools=args.strict_tools)
    else:
        ga_checks(strict_tools=args.strict_tools)

    print(f"[release-gate] {args.stage.upper()} checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
