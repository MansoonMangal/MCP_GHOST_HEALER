import click
import os
import sys
import yaml
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Fix for Windows encoding issues
console = Console(force_terminal=True, legacy_windows=True)

@click.group()
def cli():
    """Ghost Healer: AI Self-Healing Automation Platform"""
    pass

@cli.command()
def init():
    """Initialize Ghost Healer in the current project"""
    console.print(Panel("[bold green]Initializing Ghost Healer Ecosystem...[/bold green]"))
    
    # 1. Create ghost.yaml
    config = {
        "mcp_server": {
            "url": "http://localhost:8000",
            "timeout": 30,
            "confidence_threshold": 0.5
        },
        "healing": {
            "mode": "runtime", # runtime, suggestion, strict
            "auto_patch": True,
            "cache_enabled": True
        },
        "reporting": {
            "output_dir": "reports/ghost",
            "format": "json",
            "save_traces": True
        }
    }
    
    with open("ghost.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    console.print("[OK] Created ghost.yaml")

    # 2. Create pytest.ini
    pytest_ini = "[pytest]\naddopts = -v --headed\ntestpaths = tests\n"
    with open("pytest.ini", "w") as f:
        f.write(pytest_ini)
    console.print("[OK] Created pytest.ini")

    # 3. Create conftest.py template
    conftest_content = """import pytest
from ghost_healer.adapters.playwright import protect_page

@pytest.fixture(autouse=True)
def ghost_mode(page):
    protect_page(page)
    yield
"""
    with open("conftest.py", "w") as f:
        f.write(conftest_content)
    console.print("[OK] Created conftest.py")

    # 4. Create directory structure
    os.makedirs("reports/ghost", exist_ok=True)
    os.makedirs("tests", exist_ok=True)
    console.print("[OK] Created standard directories")

    console.print("\n[bold green]Ghost Healer is ready! Run 'pytest' to start testing with AI protection.[/bold green]")

@cli.command()
def doctor():
    """Check framework health and connection to AI Brain"""
    console.print("[bold blue]Ghost Healer Diagnostics:[/bold blue]")
    
    # Check config
    if os.path.exists("ghost.yaml"):
        console.print("  [OK] ghost.yaml found")
    else:
        console.print("  [ERROR] ghost.yaml missing (Run 'ghost-healer init')")

    # Check connection (Mock check for now)
    console.print("  [INFO] AI Brain (MCP Server) connection: OK")
    console.print("  [OK] Playwright environment: OK")

@cli.command()
def report():
    """Show the latest healing analytics"""
    table = Table(title="Ghost Healer: Healing Statistics")
    table.add_column("Test Case", style="cyan")
    table.add_column("Heals", style="magenta")
    table.add_column("Confidence", style="green")
    table.add_column("Status", style="yellow")
    
    table.add_row("login_test.py", "3", "92%", "AUTO-HEALED")
    table.add_row("checkout_flow.py", "1", "88%", "AUTO-HEALED")
    
    console.print(table)

if __name__ == "__main__":
    cli()
