"""
AEGISCORE — CLI Tool
Self-Hosted AI Security Intelligence Platform CLI
Command-line interface for scanning, managing, risk forecasting, fix generation, and reporting.
Built with Click + Rich for production-grade terminal UX.
Author: Mohamed Adhnaan J M | BYTEAEGIS
"""

import asyncio
import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from uuid import UUID

import click
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()

API_BASE = os.environ.get("AEGISCORE_API_URL", "http://localhost:8000/api/v1")
TOKEN_FILE = os.path.expanduser("~/.aegiscore_token")


def get_token():
    """Read stored JWT token."""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        except OSError:
            return None
    return None


def save_token(token: str):
    """Save JWT token to disk."""
    try:
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(token)
    except OSError as e:
        console.print(f"[yellow]Warning: Could not save token to {TOKEN_FILE}: {e}[/yellow]")


def clear_token():
    """Remove stored JWT token."""
    if os.path.exists(TOKEN_FILE):
        try:
            os.remove(TOKEN_FILE)
        except OSError:
            pass


def api_headers():
    """Build authorization headers."""
    token = get_token()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def extract_error_detail(response: httpx.Response) -> str:
    """Format API error responses into clear human-readable messages."""
    try:
        data = response.json()
        if isinstance(data, dict):
            detail = data.get("detail")
            if isinstance(detail, list):
                # Pydantic 422 validation errors
                msgs = []
                for item in detail:
                    loc = ".".join(str(x) for x in item.get("loc", []))
                    msg = item.get("msg", "")
                    msgs.append(f"{loc}: {msg}" if loc else msg)
                return "; ".join(msgs)
            elif detail:
                return str(detail)
            return str(data)
    except Exception:
        pass
    return response.text or f"HTTP {response.status_code}"


def api_get(endpoint: str, params=None):
    """Synchronous GET request to the API."""
    url = f"{API_BASE}{endpoint}"
    try:
        response = httpx.get(url, params=params, headers=api_headers(), timeout=30)
        if response.status_code == 401:
            console.print("[red]Session expired or not authenticated. Run: aegiscore login[/red]")
            sys.exit(1)
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError:
        console.print(f"[red]Cannot connect to AEGISCORE API at {API_BASE}. Is the server running?[/red]")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        detail = extract_error_detail(e.response)
        console.print(f"[red]API Error ({e.response.status_code}): {detail}[/red]")
        sys.exit(1)


def api_post(endpoint: str, data=None):
    """Synchronous POST request to the API."""
    url = f"{API_BASE}{endpoint}"
    try:
        response = httpx.post(url, json=data, headers=api_headers(), timeout=60)
        if response.status_code == 401:
            if "/auth/login" in endpoint:
                detail = extract_error_detail(response)
                console.print(f"[red]Authentication failed: {detail}[/red]")
            else:
                console.print("[red]Session expired or not authenticated. Run: aegiscore login[/red]")
            sys.exit(1)
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError:
        console.print(f"[red]Cannot connect to AEGISCORE API at {API_BASE}. Is the server running?[/red]")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        detail = extract_error_detail(e.response)
        console.print(f"[red]API Error ({e.response.status_code}): {detail}[/red]")
        sys.exit(1)


# ── CLI Root Group ──────────────────────────────────────────────────────────


@click.group()
@click.version_option(version="1.0.0", prog_name="aegiscore")
def cli():
    """AEGISCORE — Self-Hosted AI Security Intelligence Platform CLI"""
    pass


# ── Auth Commands ───────────────────────────────────────────────────────────


@cli.group(name="auth")
def auth_group():
    """Manage authentication sessions."""
    pass


def perform_login(email: str | None, password: str | None, token: str | None):
    if token:
        save_token(token)
        console.print(Panel(
            "[green]Authenticated via direct JWT token[/green]",
            title="AEGISCORE Auth",
            border_style="green",
        ))
        return

    if not email:
        email = click.prompt("Email")
    if not password:
        password = click.prompt("Password", hide_input=True)

    try:
        data = api_post("/auth/login", {"email": email, "password": password})
        save_token(data["access_token"])
        console.print(Panel(
            f"[green]Authenticated successfully as [bold]{email}[/bold][/green]\n"
            f"Token stored at ~/.aegiscore_token",
            title="AEGISCORE Login",
            border_style="green",
        ))
    except Exception as e:
        console.print(f"[red]Login failed: {e}[/red]")


@cli.command(name="login")
@click.option("--email", default=None, help="User email address")
@click.option("--password", default=None, help="Password")
@click.option("--token", default=None, help="Direct access token")
def login_cmd(email, password, token):
    """Authenticate with AEGISCORE platform."""
    perform_login(email, password, token)


@auth_group.command(name="login")
@click.option("--email", default=None, help="User email address")
@click.option("--password", default=None, help="Password")
@click.option("--token", default=None, help="Direct access token")
def auth_login(email, password, token):
    """Authenticate with AEGISCORE platform."""
    perform_login(email, password, token)


@cli.command(name="logout")
def logout_cmd():
    """Clear stored authentication token."""
    clear_token()
    console.print("[yellow]Successfully logged out. Stored token cleared.[/yellow]")


@auth_group.command(name="logout")
def auth_logout():
    """Clear stored authentication token."""
    clear_token()
    console.print("[yellow]Successfully logged out. Stored token cleared.[/yellow]")


@cli.command(name="whoami")
def whoami_cmd():
    """Display currently authenticated user profile."""
    data = api_get("/auth/me")
    table = Table(title="Current User Profile", border_style="dim")
    table.add_column("Field", style="cyan")
    table.add_column("Value")

    table.add_row("Full Name", data.get("full_name", ""))
    table.add_row("Email", data.get("email", ""))
    table.add_row("User ID", data.get("id", ""))
    table.add_row("Status", "[green]Active[/green]" if data.get("is_active") else "[red]Inactive[/red]")
    table.add_row("Created At", str(data.get("created_at", "")))
    console.print(table)


@auth_group.command(name="whoami")
def auth_whoami():
    """Display currently authenticated user profile."""
    whoami_cmd()


# ── Repositories Commands ───────────────────────────────────────────────────


@cli.command(name="repos")
def repos_cmd():
    """List connected repositories."""
    data = api_get("/repos")
    if not data:
        console.print("[dim]No connected repositories found for your teams.[/dim]")
        return

    table = Table(title=f"Connected Repositories ({len(data)})", border_style="dim")
    table.add_column("Name", style="cyan bold")
    table.add_column("Branch", style="dim")
    table.add_column("Repository ID", style="dim")
    table.add_column("Last Scan", style="white")

    for r in data:
        table.add_row(
            r.get("name", ""),
            r.get("default_branch", "main"),
            r.get("id", ""),
            r.get("last_scan_at", "Never") or "Never",
        )
    console.print(table)


# ── Scan Commands ───────────────────────────────────────────────────────────


@cli.command(name="scan")
@click.option("--repo-id", required=True, help="Repository UUID")
@click.option("--commit", default=None, help="Commit SHA to scan (auto-generated if omitted)")
@click.option("--branch", default="main", help="Branch name")
@click.option("--scanners", default="semgrep,bandit,trivy", help="Comma-separated scanners")
@click.option("--wait", is_flag=True, help="Wait and stream scan progress until complete")
def scan_cmd(repo_id, commit, branch, scanners, wait):
    """Trigger a security scan for a repository."""
    scanner_list = [s.strip() for s in scanners.split(",") if s.strip()]

    with console.status("[bold blue]Triggering security scan...[/bold blue]"):
        data = api_post("/scans/trigger", {
            "repo_id": repo_id,
            "commit_sha": commit,
            "branch": branch,
            "scanners": scanner_list,
        })

    scan_id = data["scan_id"]
    console.print(Panel(
        f"[green]Scan Queued Successfully[/green]\n"
        f"Scan ID: [cyan]{scan_id}[/cyan]\n"
        f"Branch: [white]{branch}[/white]\n"
        f"Scanners: [white]{', '.join(scanner_list)}[/white]",
        title="AEGISCORE Scan Orchestration",
        border_style="green",
    ))

    if wait:
        console.print("\n[bold]Waiting for scan completion...[/bold]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Running scanners...", total=100)
            while True:
                time.sleep(3)
                status_data = api_get(f"/scans/{scan_id}/status")
                overall_status = status_data.get("status", "queued")

                tasks = status_data.get("tasks", [])
                completed_count = sum(1 for t in tasks if t.get("status") in ("completed", "failed"))
                total_tasks = max(1, len(tasks))
                pct = int((completed_count / total_tasks) * 100)
                progress.update(task, completed=pct, description=f"Status: {overall_status.upper()} ({completed_count}/{total_tasks} scanners done)")

                if overall_status in ("completed", "failed"):
                    break

        # Show final findings summary
        final_scan = api_get(f"/scans/{scan_id}")
        table = Table(title=f"Scan Finished: {final_scan.get('status', '').upper()}", border_style="dim")
        table.add_column("Metric", style="cyan")
        table.add_column("Value")

        table.add_row("Total Findings", str(final_scan.get("total_findings", 0)))
        table.add_row("Critical", f"[red]{final_scan.get('critical_count', 0)}[/red]")
        table.add_row("High", f"[yellow]{final_scan.get('high_count', 0)}[/yellow]")
        table.add_row("Medium", f"[blue]{final_scan.get('medium_count', 0)}[/blue]")
        table.add_row("Low", f"[green]{final_scan.get('low_count', 0)}[/green]")
        console.print(table)


@cli.command(name="status")
@click.option("--scan-id", default=None, help="Check status for a specific scan ID")
@click.option("--repo-id", default=None, help="Filter scans by repository ID")
@click.option("--watch", is_flag=True, help="Live refresh every 3 seconds")
def status_cmd(scan_id, repo_id, watch):
    """Check active and recent scan status across the organization."""
    if scan_id:
        data = api_get(f"/scans/{scan_id}/status")
        table = Table(title=f"Scan Status: {scan_id}", border_style="dim")
        table.add_column("Scanner", style="cyan")
        table.add_column("Status")
        table.add_column("Findings", justify="right")

        status_colors = {"completed": "green", "running": "blue", "queued": "dim", "failed": "red"}
        for t in data.get("tasks", []):
            st = t.get("status", "unknown")
            color = status_colors.get(st, "white")
            table.add_row(t.get("scanner", "?"), f"[{color}]{st}[/{color}]", str(t.get("findings_count", 0)))
        console.print(table)
        console.print(f"Overall: {data.get('status', 'unknown').upper()} | Total findings: {data.get('total_findings', 0)}")
        return

    # Org-wide scans list
    def render_scans_table():
        params = {"limit": 15}
        if repo_id:
            params["repo_id"] = repo_id
        data = api_get("/scans", params=params)
        scans = data.get("scans", [])

        table = Table(title=f"Recent Scans ({len(scans)})", border_style="dim")
        table.add_column("Scan ID", style="cyan")
        table.add_column("Branch", style="dim")
        table.add_column("Status")
        table.add_column("Total Findings", justify="right")
        table.add_column("CRIT / HIGH", justify="right")
        table.add_column("Duration")

        status_colors = {"completed": "green", "running": "blue", "queued": "dim", "failed": "red"}
        for s in scans:
            st = s.get("status", "unknown")
            color = status_colors.get(st, "white")
            dur = f"{s.get('duration_ms', 0) / 1000:.1f}s" if s.get("duration_ms") else "—"
            crit_high = f"[red]{s.get('critical_count', 0)}[/red] / [yellow]{s.get('high_count', 0)}[/yellow]"
            table.add_row(
                s.get("id", "")[:8] + "...",
                s.get("branch", ""),
                f"[{color}]{st}[/{color}]",
                str(s.get("total_findings", 0)),
                crit_high,
                dur,
            )
        return table

    if not watch:
        console.print(render_scans_table())
    else:
        console.print("[dim]Watching live scans (Ctrl+C to stop)...[/dim]")
        try:
            while True:
                console.clear()
                console.print(render_scans_table())
                time.sleep(3)
        except KeyboardInterrupt:
            console.print("\n[yellow]Watch stopped.[/yellow]")


# ── Findings Commands ───────────────────────────────────────────────────────


@cli.command(name="findings")
@click.option("--repo-id", default=None, help="Filter by repository UUID")
@click.option("--severity", default=None, type=click.Choice(["CRITICAL", "HIGH", "MEDIUM", "LOW"], case_sensitive=False))
@click.option("--scanner", default=None, type=click.Choice(["semgrep", "bandit", "trivy"], case_sensitive=False))
@click.option("--rule", default=None, help="Filter by rule ID")
@click.option("--limit", default=25, help="Maximum findings to return")
def findings_cmd(repo_id, severity, scanner, rule, limit):
    """List detected security vulnerabilities."""
    params = {"limit": limit}
    if repo_id:
        params["repo_id"] = repo_id
    if severity:
        params["severity"] = severity.upper()
    if scanner:
        params["scanner"] = scanner.lower()
    if rule:
        params["rule_id"] = rule

    data = api_get("/findings", params)
    if not data or not isinstance(data, dict):
        return
    finding_list = data.get("findings", [])

    if not finding_list:
        console.print("[dim]No findings match the specified criteria.[/dim]")
        return

    table = Table(title=f"Security Findings ({data.get('total', len(finding_list))} total)", border_style="dim")
    table.add_column("SEV", width=8)
    table.add_column("Location", style="cyan")
    table.add_column("Scanner", style="dim")
    table.add_column("Rule ID")
    table.add_column("Fix", justify="center")

    sev_colors = {"CRITICAL": "red bold", "HIGH": "yellow bold", "MEDIUM": "blue", "LOW": "green"}

    for f in finding_list:
        sev = f.get("severity", "?")
        color = sev_colors.get(sev, "white")
        loc = f"{f.get('file_path', '?')}:{f.get('line_number', 0)}"
        fix_badge = "[green]YES[/green]" if f.get("has_fix") else "[dim]-[/dim]"
        table.add_row(
            f"[{color}]{sev}[/{color}]",
            loc[:48],
            f.get("scanner", "?"),
            f.get("rule_id", "?")[:36],
            fix_badge,
        )

    console.print(table)


# ── Predictive Risk Forecasting Commands ────────────────────────────────────


@cli.command(name="predict")
@click.option("--repo-id", required=True, help="Repository UUID")
@click.option("--top", default=10, help="Show top N riskiest files")
@click.option("--min-score", default=0.2, help="Minimum risk score threshold (0.0 to 1.0)")
@click.option("--file", "target_file", default=None, help="Score a specific file only")
def predict_cmd(repo_id, top, min_score, target_file):
    """Forecast file vulnerability likelihood using organizational ML model."""
    data = api_get("/risk/heatmap", {"repo_id": repo_id, "min_score": min_score, "limit": 100})
    if not data or not isinstance(data, dict):
        return
    files = data.get("files", [])

    if target_file:
        files = [f for f in files if target_file in f.get("file_path", "")]

    files = files[:top]

    if not files:
        console.print("[dim]No files meet the risk score criteria for this repository.[/dim]")
        return

    table = Table(title="Vulnerability Risk Forecast (ML Random Forest)", border_style="dim")
    table.add_column("File Path", style="cyan bold")
    table.add_column("Score", justify="right")
    table.add_column("Likelihood Meter", width=22)
    table.add_column("Category")

    for f in files:
        score = float(f.get("score", 0.0))
        if score >= 0.8:
            color = "red"
            cat = "CRITICAL RISK"
        elif score >= 0.6:
            color = "yellow"
            cat = "HIGH RISK"
        elif score >= 0.4:
            color = "blue"
            cat = "MEDIUM RISK"
        else:
            color = "green"
            cat = "MINIMAL RISK"

        bar_len = int(score * 15)
        bar = "#" * bar_len + "-" * (15 - bar_len)

        table.add_row(
            f.get("file_path", "")[:45],
            f"[{color}]{score:.2f}[/{color}]",
            f"[{color}]{bar}[/{color}]",
            f"[{color}]{cat}[/{color}]",
        )

    console.print(table)


@cli.command(name="risk")
@click.option("--repo-id", required=True, help="Repository UUID")
@click.option("--min-score", default=0.3, help="Minimum risk score")
@click.option("--limit", default=20, help="Max results")
def risk_cmd(repo_id, min_score, limit):
    """Display risk heatmap for a repository (alias for predict)."""
    click.get_current_context().invoke(predict_cmd, repo_id=repo_id, top=limit, min_score=min_score, target_file=None)


# ── AI Fix Generation Commands ──────────────────────────────────────────────


@cli.command(name="fix")
@click.option("--finding-id", default=None, help="Security Finding UUID")
@click.option("--scan-id", default=None, help="Fetch all fixes for a scan UUID")
@click.option("--generate", is_flag=True, help="Trigger on-demand generation if fix does not exist")
@click.option("--apply", is_flag=True, help="Apply fix and mark as resolved in platform")
def fix_cmd(finding_id, scan_id, generate, apply):
    """Retrieve, generate, or apply local AI-generated code patches."""
    if not finding_id and not scan_id:
        # List all available fixes
        data = api_get("/fixes", {"limit": 20})
        fixes = data.get("fixes", [])
        if not fixes:
            console.print("[dim]No AI fix suggestions available. Run a scan with CRITICAL or HIGH findings.[/dim]")
            return

        table = Table(title="AI Fix Suggestions", border_style="dim")
        table.add_column("Fix ID", style="dim")
        table.add_column("Finding ID", style="cyan")
        table.add_column("Location")
        table.add_column("Confidence")
        table.add_column("Applied")

        for fix in fixes:
            conf_color = "green" if fix.get("confidence") == "high" else "yellow"
            app_color = "green" if fix.get("applied") else "dim"
            loc = f"{fix.get('file_path', '—')}:{fix.get('line_number', 0)}" if fix.get("file_path") else "—"
            table.add_row(
                fix.get("id", "")[:8] + "...",
                fix.get("finding_id", "")[:8] + "...",
                loc,
                f"[{conf_color}]{fix.get('confidence')}[/{conf_color}]",
                f"[{app_color}]{'Yes' if fix.get('applied') else 'Pending'}[/{app_color}]",
            )
        console.print(table)
        console.print("\nRun: [cyan]aegiscore fix --finding-id <UUID>[/cyan] to review code diff.")
        return

    if finding_id:
        # Check if fix exists
        data = api_get("/fixes", {"finding_id": finding_id})
        fixes = data.get("fixes", [])
        fix = fixes[0] if fixes else None

        if not fix and generate:
            with console.status("[bold blue]Generating AI fix with local Ollama LLM...[/bold blue]"):
                fix = api_post("/fixes/generate", {"finding_id": finding_id})
        elif not fix:
            console.print("[yellow]No fix generated yet for this finding. Use --generate to create one.[/yellow]")
            return

        diff_text = fix.get("unified_diff", "")
        explanation = fix.get("explanation", "")
        confidence = fix.get("confidence", "medium")

        console.print(Panel(
            f"[bold]Model:[/bold] {fix.get('model_used')}  |  "
            f"[bold]Confidence:[/bold] [{ 'green' if confidence == 'high' else 'yellow' }]{confidence.upper()}[/]  |  "
            f"[bold]Status:[/bold] {'[green]Applied[/green]' if fix.get('applied') else '[yellow]Pending Review[/yellow]'}",
            title="AI Fix Suggestion",
            border_style="blue",
        ))

        console.print("\n[bold]Unified Diff Patch:[/bold]")
        syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
        console.print(syntax)

        console.print("\n[bold]Explanation:[/bold]")
        console.print(explanation)

        if apply:
            with console.status("[bold blue]Marking fix as applied...[/bold blue]"):
                api_post(f"/fixes/{fix['id']}/apply")
            console.print("\n[green]✓ Fix marked as applied successfully in AEGISCORE platform.[/green]")


# ── Cross-Repository Correlation Commands ───────────────────────────────────


@cli.command(name="correlate")
@click.option("--rule", default=None, help="Filter by vulnerability rule ID")
@click.option("--severity", default=None, help="Filter by severity level")
def correlate_cmd(rule, severity):
    """Display cross-repository correlated security findings across the organization."""
    params = {}
    if rule:
        params["rule_id"] = rule
    if severity:
        params["severity"] = severity

    data = api_get("/correlations", params)
    correlations = data.get("correlations", [])

    if not correlations:
        console.print("[dim]No cross-repo correlation groups detected across your organization.[/dim]")
        return

    console.print(Panel(
        f"[bold]Detected {len(correlations)} Cross-Repository Correlation Group(s)[/bold]\n"
        "Vulnerabilities that share identical signatures propagated across multiple codebases.",
        title="AEGISCORE Correlation Intelligence",
        border_style="cyan",
    ))

    for group in correlations:
        sev = group.get("severity", "CRITICAL")
        sev_color = "red" if sev == "CRITICAL" else "yellow" if sev == "HIGH" else "blue"

        table = Table(
            title=f"Rule: [{sev_color}]{group.get('rule_id')}[/{sev_color}] ({group.get('repos_affected')} repos affected)",
            border_style="dim",
        )
        table.add_column("Repository", style="cyan bold")
        table.add_column("Team", style="dim")
        table.add_column("Occurrences", justify="right")
        table.add_column("Files")

        for r in group.get("repos", []):
            file_names = ", ".join(f.get("file_path", "") for f in r.get("files", [])[:3])
            table.add_row(
                r.get("repo_name", "?"),
                r.get("team_name", "?"),
                str(len(r.get("files", []))),
                file_names,
            )

        console.print(table)
        console.print("")


# ── Reporting Commands ──────────────────────────────────────────────────────


@cli.command(name="report")
@click.option("--repo-id", default=None, help="Filter findings by repository UUID")
@click.option("--scan-id", default=None, help="Filter findings by scan UUID")
@click.option("--format", "export_format", default="table", type=click.Choice(["table", "json", "csv", "markdown"]))
@click.option("--output", "output_file", default=None, help="Save report to file path")
def report_cmd(repo_id, scan_id, export_format, output_file):
    """Generate and export comprehensive security audit reports."""
    params = {"limit": 500}
    if repo_id:
        params["repo_id"] = repo_id
    if scan_id:
        params["scan_id"] = scan_id

    data = api_get("/findings", params)
    findings = data.get("findings", [])

    if export_format == "json":
        report_str = json.dumps(findings, indent=2)
    elif export_format == "csv":
        import io
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["id", "scanner", "severity", "rule_id", "file_path", "line_number", "cwe", "message"])
        writer.writeheader()
        for f in findings:
            writer.writerow({
                "id": f.get("id"),
                "scanner": f.get("scanner"),
                "severity": f.get("severity"),
                "rule_id": f.get("rule_id"),
                "file_path": f.get("file_path"),
                "line_number": f.get("line_number"),
                "cwe": f.get("cwe") or "",
                "message": f.get("message", "").replace("\n", " "),
            })
        report_str = buf.getvalue()
    elif export_format == "markdown":
        lines = [
            "# AEGISCORE Security Audit Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Total Findings: {len(findings)}",
            "",
            "| Severity | Scanner | Rule | Location | Description |",
            "|---|---|---|---|---|",
        ]
        for f in findings:
            lines.append(f"| {f.get('severity')} | {f.get('scanner')} | `{f.get('rule_id')}` | `{f.get('file_path')}:{f.get('line_number')}` | {f.get('message')[:80]} |")
        report_str = "\n".join(lines)
    else:
        # Table format to terminal
        click.get_current_context().invoke(findings_cmd, repo_id=repo_id, severity=None, scanner=None, rule=None, limit=50)
        return

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_str)
        console.print(f"[green]Report saved successfully to {output_file}[/green]")
    else:
        console.print(report_str)


# ── ML Model Commands ───────────────────────────────────────────────────────


@cli.command(name="model-status")
def model_status_cmd():
    """Display ML risk model performance metrics and training history."""
    data = api_get("/risk/model/status")

    if data.get("is_trained"):
        console.print(Panel(
            f"[green]Random Forest Model Active[/green]\n"
            f"Version: [cyan]{data.get('model_version', 'unknown')}[/cyan]\n"
            f"Training Samples: [white]{data.get('training_samples', 0)}[/white]\n"
            f"Precision: [white]{data.get('precision', 0):.3f}[/white]\n"
            f"Recall: [white]{data.get('recall', 0):.3f}[/white]\n"
            f"F1 Score: [white]{data.get('f1_score', 0):.3f}[/white]\n"
            f"Next retrain in: [yellow]{data.get('next_retrain_in', 0)}[/yellow] scans",
            title="AEGISCORE Risk Forecasting Model",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[yellow]Risk Model Not Trained Yet[/yellow]\n"
            f"Requires training data. Next automatic training in {data.get('next_retrain_in', 50)} scans.\n"
            "Run: [cyan]aegiscore model-retrain[/cyan] to trigger training.",
            title="AEGISCORE Risk Model",
            border_style="yellow",
        ))


@cli.command(name="model-retrain")
def model_retrain_cmd():
    """Trigger manual retraining of the organizational risk model."""
    with console.status("[bold blue]Retraining Random Forest model on historical scan features...[/bold blue]"):
        res = api_post("/risk/model/retrain")
    console.print(Panel(
        f"Status: [green]{res.get('status', 'completed')}[/green]\n"
        f"{res.get('message', '') or ''}\n"
        f"F1 Score: {res.get('f1_score', '—')}",
        title="Model Retraining",
        border_style="green",
    ))


# ── Health & System Commands ────────────────────────────────────────────────


@cli.command(name="health")
def health_cmd():
    """Check API and background component health status."""
    data = api_get("/api/v1/health")
    components = data.get("components", {})

    table = Table(title="AEGISCORE Platform Health", border_style="dim")
    table.add_column("Component", style="cyan")
    table.add_column("Status")

    for comp, st in components.items():
        color = "green" if "healthy" in st else "red"
        table.add_row(comp.capitalize(), f"[{color}]{st}[/{color}]")

    console.print(table)


if __name__ == "__main__":
    cli()
