import click
import os
import json
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console(force_terminal=True, legacy_windows=True)


@click.group()
def cli():
    """Ghost Healer: AI Self-Healing Automation Platform"""
    pass


@cli.command()
def init():
    """Initialize Ghost Healer in the current project"""
    console.print(Panel("[bold green]Initializing Ghost Healer Ecosystem...[/bold green]"))

    config = {
        "mcp_server": {
            "url": os.environ.get("GHOST_BRAIN_URL", "https://ghost-healer-brain.onrender.com"),
            "timeout": 30,
            "confidence_threshold": 0.5,
            "protocol": "mcp-first",
            "api_key": "",
        },
        "healing": {
            "mode": "runtime",
            "auto_patch": True,
            "cache_enabled": True,
            "selenium_fixture_names": ["driver", "browser", "webdriver", "selenium_driver"],
        },
        "reporting": {
            "output_dir": "reports/ghost",
            "format": "json",
            "save_traces": True,
        },
    }

    with open("ghost.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False)
    console.print("[OK] Created ghost.yaml")

    pytest_ini = "[pytest]\naddopts = -v\ntestpaths = tests\n"
    with open("pytest.ini", "w", encoding="utf-8") as f:
        f.write(pytest_ini)
    console.print("[OK] Created pytest.ini (pytest plugin auto-activates — no conftest required)")

    os.makedirs("reports/ghost", exist_ok=True)
    os.makedirs("tests", exist_ok=True)
    console.print("[OK] Created standard directories")
    console.print(
        "\n[bold green]Ghost Healer ready. Install SDK and run tests — zero script changes needed.[/bold green]"
    )


@cli.command()
def doctor():
    """Check framework health and connection to AI Brain (MCP-first)"""
    from ghost_healer.core.config import settings
    from ghost_healer.core.mcp_client import brain_client

    console.print("[bold blue]Ghost Healer Diagnostics[/bold blue]")

    from ghost_healer.core.config import find_ghost_yaml

    yaml_path = find_ghost_yaml()
    if yaml_path:
        console.print(f"  [OK] ghost.yaml found at {yaml_path}")
    else:
        console.print("  [WARN] ghost.yaml missing — using defaults")

    console.print(f"  [INFO] Brain URL: {settings.mcp_server.url}")
    console.print(f"  [INFO] Protocol: {settings.mcp_server.protocol}")
    console.print(f"  [INFO] Healing mode: {settings.healing.mode}")

    try:
        health = brain_client.health_check()
        console.print(f"  [OK] Brain health: {health.get('status')} v{health.get('version')}")
        console.print(f"  [OK] MCP endpoint: {health.get('mcp_endpoint', '/mcp')}")
    except Exception as exc:
        console.print(f"  [ERROR] Brain unreachable: {exc}")

    try:
        import playwright  # noqa: F401
        console.print("  [OK] Playwright installed")
    except ImportError:
        console.print("  [WARN] Playwright not installed (optional for Python PW tests)")

    console.print("  [OK] Pytest plugin: auto-loaded via entry point when ghost-healer is installed")


@cli.command()
def report():
    """Show healing analytics from Brain"""
    from ghost_healer.core.mcp_client import brain_client
    import httpx

    try:
        url = brain_client.base_url.rstrip("/") + "/api/confidence-report"
        resp = httpx.get(url, headers=brain_client._headers(), timeout=15)
        data = resp.json()
    except Exception as exc:
        console.print(f"[ERROR] Could not fetch report: {exc}")
        return

    table = Table(title="Ghost Healer: Healing Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Total healed", str(data.get("total_healed", 0)))
    table.add_row("Auto heal", str(data.get("auto_heal_count", 0)))
    table.add_row("Success rate %", str(data.get("success_rate_percent", 0)))
    table.add_row("Avg confidence", str(data.get("avg_confidence_score", 0)))
    console.print(table)


@cli.command()
@click.option("--approve-all", is_flag=True, help="Mark all pending fixes as approved.")
def review(approve_all: bool):
    """Review pending locator fixes generated in approval/suggestion modes."""
    pending_path = os.path.join("reports", "ghost", "pending-fixes.json")
    if not os.path.exists(pending_path):
        console.print("[WARN] No pending-fixes.json found.")
        return

    try:
        with open(pending_path, "r", encoding="utf-8") as f:
            rows = json.load(f)
    except Exception as exc:
        console.print(f"[ERROR] Could not read pending fixes: {exc}")
        return

    if not isinstance(rows, list) or not rows:
        console.print("[INFO] No pending fixes.")
        return

    if approve_all:
        for row in rows:
            if row.get("status") == "pending_review":
                row["status"] = "approved"
        with open(pending_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
        console.print("[OK] Marked all pending fixes as approved.")

    table = Table(title="Ghost Healer: Pending Fixes")
    table.add_column("ID", style="cyan")
    table.add_column("Old Locator", style="magenta")
    table.add_column("Suggested", style="green")
    table.add_column("Confidence", style="yellow")
    table.add_column("Status", style="white")
    for row in rows[:25]:
        table.add_row(
            str(row.get("id") or row.get("pending_id", "")),
            str(row.get("old_locator", ""))[:40],
            str(row.get("suggested_locator", ""))[:40],
            str(row.get("confidence", "")),
            str(row.get("status", "")),
        )
    console.print(table)


if __name__ == "__main__":
    cli()
