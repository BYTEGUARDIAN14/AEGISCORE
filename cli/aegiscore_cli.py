"""
AEGISCORE — CLI Tool
Command-line interface for scanning, managing, and monitoring.
Built with Click + Rich for production-grade terminal UX.
"""

import asyncio
import json
import os
import sys
from datetime import datetime

import click
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.text import Text

console = Console()

API_BASE = os.environ.get("AEGISCORE_API_URL", "http://localhost:8000/api/v1")
TOKEN_FILE = os.path.expanduser("~/.aegiscore_token")


def get_token():
    """Read stored JWT token."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None


def save_token(token):
    """Save JWT token to disk."""
    with open(TOKEN_FILE, "w") as f:
        f.write(token)


def clear_token():
    """Remove stored JWT token."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)


def api_headers():
    """Build authorization headers."""
    token = get_token()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def api_get(endpoint, params=None):
    """Synchronous GET request to the API."""
    url = f"{API_BASE}{endpoint}"
    response = httpx.get(url, params=params, headers=api_headers(), timeout=30)
    if response.status_code == 401:
        console.print("[red]Session expired. Run: aegiscore login[/red]")
        sys.exit(1)
    response.raise_for_status()
    return response.json()


def api_post(endpoint, data=None):
    """Synchronous POST request to the API."""
    url = f"{API_BASE}{endpoint}"
    response = httpx.post(url, json=data, headers=api_headers(), timeout=30)
    if response.status_code == 401:
        console.print("[red]Session expired. Run: aegiscore login[/red]")
        sys.exit(1)
    response.raise_for_status()
    return response.json()


# ── CLI Group ───────────────────────────────────────────────────────────────


@click.group()
@click.version_option(version="1.0.0", prog_name="aegiscore")
def cli():
    """AEGISCORE — Self-Hosted AI Security Intelligence Platform CLI"""
    pass


# ── Auth Commands ───────────────────────────────────────────────────────────


@cli.command()
@click.option("--email", prompt="Email", help="User email address")
@click.option("--password", prompt="Password", hide_input=True, help="Password")
def login(email, password):
    """Authenticate with the AEGISCORE platform."""
    try:
        data = api_post("/auth/login", {"email": email, "password": password})
        save_token(data["access_token"])
        console.print(Panel(
            f"[green]Authenticated as {email}[/green]",
            title="AEGISCORE Login",
            border_style="green",
        ))
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            console.print("[red]Invalid credentials[/red]")
        else:
            console.print(f"[red]Login failed: {e}[/red]")
    except httpx.ConnectError:
        console.print(f"[red]Cannot connect to {API_BASE}[/red]")


@cli.command()
def logout():
    """Clear stored authentication token."""
    clear_token()
    console.print("[yellow]Logged out[/yellow]")


@cli.command()
def whoami():
    """Display current authenticated user."""
    try:
        data = api_get("/auth/me")
        table = Table(title="Current User", border_style="dim")
        table.add_column("Field", style="dim")
        table.add_column("Value")

        table.add_row("Email", data.get("email", ""))
        table.add_row("Name", data.get("full_name", ""))
        table.add_row("Role", data.get("role", ""))
        table.add_row("ID", data.get("id", "")[:8] + "...")
        console.print(table)
    except httpx.HTTPStatusError:
        console.print("[red]Not authenticated. Run: aegiscore login[/red]")
    except httpx.ConnectError:
        console.print(f"[red]Cannot connect to {API_BASE}[/red]")


# ── Scan Commands ───────────────────────────────────────────────────────────


@cli.command()
@click.option("--repo-id", required=True, help="Repository UUID")
@click.option("--commit", default=None, help="Commit SHA to scan")
@click.option("--branch", default="main", help="Branch name")
@click.option("--scanners", default="semgrep,bandit,trivy", help="Comma-separated scanners")
def scan(repo_id, commit, branch, scanners):
    """Trigger a security scan for a repository."""
    scanner_list = [s.strip() for s in scanners.split(",")]

    try:
        with console.status("[bold blue]Triggering scan...[/bold blue]"):
            data = api_post("/scans/trigger", {
                "repo_id": repo_id,
                "commit_sha": commit,
                "branch": branch,
                "scanners": scanner_list,
            })

        console.print(Panel(
            f"[green]Scan queued[/green]\n"
            f"Scan ID: [cyan]{data['scan_id']}[/cyan]\n"
            f"Scanners: {', '.join(scanner_list)}\n"
            f"Tasks: {len(data.get('task_ids', []))}",
            title="Scan Triggered",
            border_style="green",
        ))
    except httpx.HTTPStatusError as e:
        error = e.response.json().get("detail", str(e))
        console.print(f"[red]Scan failed: {error}[/red]")
    except httpx.ConnectError:
        console.print(f"[red]Cannot connect to {API_BASE}[/red]")


@cli.command(name="scan-status")
@click.option("--scan-id", required=True, help="Scan UUID")
def scan_status(scan_id):
    """Check the status of a running scan."""
    try:
        data = api_get(f"/scans/{scan_id}/status")

        table = Table(title=f"Scan Status: {scan_id[:8]}...", border_style="dim")
        table.add_column("Scanner", style="cyan")
        table.add_column("Status")
        table.add_column("Findings", justify="right")

        status_colors = {
            "completed": "green",
            "running": "blue",
            "queued": "dim",
            "failed": "red",
        }

        for task in data.get("tasks", []):
            status_val = task.get("status", "unknown")
            color = status_colors.get(status_val, "white")
            table.add_row(
                task.get("scanner", "?"),
                f"[{color}]{status_val}[/{color}]",
                str(task.get("findings_count", 0)),
            )

        console.print(table)
        console.print(f"\nOverall: [{status_colors.get(data.get('status', ''), 'white')}]{data.get('status', 'unknown')}[/] | Total findings: {data.get('total_findings', 0)}")
    except httpx.HTTPStatusError as e:
        console.print(f"[red]Not found: {e}[/red]")


# ── Findings Commands ───────────────────────────────────────────────────────


@cli.command()
@click.option("--severity", default=None, type=click.Choice(["CRITICAL", "HIGH", "MEDIUM", "LOW"]))
@click.option("--scanner", default=None, type=click.Choice(["semgrep", "bandit", "trivy"]))
@click.option("--limit", default=20, help="Max results")
def findings(severity, scanner, limit):
    """List security findings."""
    try:
        params = {"limit": limit}
        if severity:
            params["severity"] = severity
        if scanner:
            params["scanner"] = scanner

        data = api_get("/findings", params)
        finding_list = data.get("findings", [])

        if not finding_list:
            console.print("[dim]No findings match your criteria.[/dim]")
            return

        table = Table(title=f"Security Findings ({data.get('total', 0)} total)", border_style="dim")
        table.add_column("SEV", width=6)
        table.add_column("File", style="cyan")
        table.add_column("Scanner")
        table.add_column("Rule")
        table.add_column("Fix", justify="center")

        sev_colors = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "blue", "LOW": "green"}

        for f in finding_list:
            sev = f.get("severity", "?")
            color = sev_colors.get(sev, "white")
            file_loc = f"{f.get('file_path', '?')}:{f.get('line_number', 0)}"
            fix_indicator = "✓" if f.get("has_fix") else "—"

            table.add_row(
                f"[{color}]{sev[:4]}[/{color}]",
                file_loc[:50],
                f.get("scanner", "?"),
                f.get("rule_id", "?")[:30],
                fix_indicator,
            )

        console.print(table)
    except httpx.ConnectError:
        console.print(f"[red]Cannot connect to {API_BASE}[/red]")


# ── Risk Commands ───────────────────────────────────────────────────────────


@cli.command()
@click.option("--repo-id", required=True, help="Repository UUID")
@click.option("--min-score", default=0.3, help="Minimum risk score")
@click.option("--limit", default=20, help="Max results")
def risk(repo_id, min_score, limit):
    """Display risk heatmap for a repository."""
    try:
        data = api_get("/risk/heatmap", {
            "repo_id": repo_id,
            "min_score": min_score,
            "limit": limit,
        })

        files = data.get("files", [])
        if not files:
            console.print("[dim]No risk data available.[/dim]")
            return

        table = Table(title="Risk Heatmap", border_style="dim")
        table.add_column("File", style="cyan")
        table.add_column("Score", justify="right")
        table.add_column("Risk", width=20)

        for f in files:
            score = f.get("score", 0)
            if score >= 0.8:
                color = "red"
                label = "CRITICAL"
            elif score >= 0.6:
                color = "yellow"
                label = "HIGH"
            elif score >= 0.4:
                color = "blue"
                label = "MEDIUM"
            else:
                color = "green"
                label = "MINIMAL"

            bar_width = int(score * 15)
            bar = "█" * bar_width + "░" * (15 - bar_width)

            table.add_row(
                f.get("file_path", "?")[:40],
                f"[{color}]{score:.2f}[/{color}]",
                f"[{color}]{bar}[/{color}]",
            )

        console.print(table)
    except httpx.ConnectError:
        console.print(f"[red]Cannot connect to {API_BASE}[/red]")


# ── Model Commands ──────────────────────────────────────────────────────────


@cli.command(name="model-status")
def model_status():
    """Display ML risk model status."""
    try:
        data = api_get("/risk/model/status")

        if data.get("is_trained"):
            console.print(Panel(
                f"[green]Model Trained[/green]\n"
                f"Version: [cyan]{data.get('model_version', '?')}[/cyan]\n"
                f"Samples: {data.get('training_samples', 0)}\n"
                f"Precision: {data.get('precision', 0):.3f}\n"
                f"Recall: {data.get('recall', 0):.3f}\n"
                f"F1 Score: {data.get('f1_score', 0):.3f}\n"
                f"Next retrain in: {data.get('next_retrain_in', '?')} scans",
                title="ML Risk Model",
                border_style="blue",
            ))
        else:
            console.print(Panel(
                f"[yellow]Model Not Trained[/yellow]\n"
                f"Requires minimum scan data before training.",
                title="ML Risk Model",
                border_style="yellow",
            ))
    except httpx.ConnectError:
        console.print(f"[red]Cannot connect to {API_BASE}[/red]")


# ── Health Commands ─────────────────────────────────────────────────────────


@cli.command()
def health():
    """Check platform health status."""
    try:
        data = api_get("/health")
        components = data.get("components", {})

        table = Table(title="AEGISCORE Health", border_style="dim")
        table.add_column("Component")
        table.add_column("Status")

        for component, status_val in components.items():
            color = "green" if status_val == "healthy" else "red"
            table.add_row(component, f"[{color}]{status_val}[/{color}]")

        overall_color = "green" if data.get("status") == "healthy" else "yellow"
        console.print(table)
        console.print(f"\nOverall: [{overall_color}]{data.get('status', 'unknown')}[/{overall_color}] | Version: {data.get('version', '?')}")
    except httpx.ConnectError:
        console.print(f"[red]Cannot connect to {API_BASE}[/red]")


if __name__ == "__main__":
    cli()
