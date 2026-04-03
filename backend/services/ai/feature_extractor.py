"""
AEGISCORE — Feature Extractor Service
Extracts ML features from git history, code complexity, and scan history.
"""

import asyncio
import math
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def extract_features(
    repo_path: str,
    file_path: str,
    db_session: AsyncSession,
) -> dict[str, float]:
    """
    Extract 8 ML features for a specific file in a repository.

    Features:
        1. commit_frequency_30d   — Commits touching file in last 30 days
        2. author_count           — Distinct authors who modified file
        3. avg_diff_size          — Average lines changed per commit
        4. past_vuln_count        — Total findings ever for this file
        5. days_since_last_vuln   — Days since most recent finding
        6. file_complexity_score  — Cyclomatic complexity (0.0–100.0)
        7. import_risk_score      — Import risk (default 0.5)
        8. test_coverage_ratio    — Test coverage (default 0.5)

    Args:
        repo_path: Absolute path to the cloned repository.
        file_path: Relative file path within the repository.
        db_session: Async database session for scan history queries.

    Returns:
        Dictionary with all 8 features as floats.
    """
    features: dict[str, float] = {
        "commit_frequency_30d": 0.0,
        "author_count": 0.0,
        "avg_diff_size": 0.0,
        "past_vuln_count": 0.0,
        "days_since_last_vuln": 9999.0,
        "file_complexity_score": 0.0,
        "import_risk_score": 0.5,
        "test_coverage_ratio": 0.5,
    }

    # ── Git history features ────────────────────────────────────────────
    try:
        git_features = await _extract_git_features(repo_path, file_path)
        features.update(git_features)
    except (RuntimeError, FileNotFoundError, OSError):
        pass

    # ── Scan history features ───────────────────────────────────────────
    try:
        scan_features = await _extract_scan_history_features(
            file_path, db_session
        )
        features.update(scan_features)
    except Exception:
        pass

    # ── Code complexity features ────────────────────────────────────────
    try:
        complexity = await _extract_complexity(repo_path, file_path)
        features["file_complexity_score"] = complexity
    except Exception:
        pass

    return features


async def _extract_git_features(
    repo_path: str,
    file_path: str,
) -> dict[str, float]:
    """
    Extract git log based features using async subprocess.
    """
    result: dict[str, float] = {}

    # 1. Commit frequency in last 30 days
    thirty_days_ago = (
        datetime.now(timezone.utc) - timedelta(days=30)
    ).strftime("%Y-%m-%d")

    try:
        process = await asyncio.create_subprocess_exec(
            "git", "log",
            "--since", thirty_days_ago,
            "--oneline",
            "--follow",
            "--", file_path,
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(process.communicate(), timeout=30)
        lines = stdout.decode("utf-8").strip().split("\n")
        result["commit_frequency_30d"] = float(
            len([l for l in lines if l.strip()])
        )
    except (asyncio.TimeoutError, FileNotFoundError):
        result["commit_frequency_30d"] = 0.0

    # 2. Distinct author count
    try:
        process = await asyncio.create_subprocess_exec(
            "git", "log",
            "--format=%ae",
            "--follow",
            "--", file_path,
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(process.communicate(), timeout=30)
        authors = set(
            line.strip()
            for line in stdout.decode("utf-8").strip().split("\n")
            if line.strip()
        )
        result["author_count"] = float(len(authors))
    except (asyncio.TimeoutError, FileNotFoundError):
        result["author_count"] = 0.0

    # 3. Average diff size
    try:
        process = await asyncio.create_subprocess_exec(
            "git", "log",
            "--numstat",
            "--format=",
            "--follow",
            "--", file_path,
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(process.communicate(), timeout=30)
        lines_output = stdout.decode("utf-8").strip().split("\n")

        total_changes = 0
        commit_count = 0

        for line in lines_output:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    added = int(parts[0]) if parts[0] != "-" else 0
                    removed = int(parts[1]) if parts[1] != "-" else 0
                    total_changes += added + removed
                    commit_count += 1
                except ValueError:
                    continue

        if commit_count > 0:
            result["avg_diff_size"] = float(total_changes / commit_count)
        else:
            result["avg_diff_size"] = 0.0
    except (asyncio.TimeoutError, FileNotFoundError):
        result["avg_diff_size"] = 0.0

    return result


async def _extract_scan_history_features(
    file_path: str,
    db_session: AsyncSession,
) -> dict[str, float]:
    """
    Extract features from historical scan findings in the database.
    """
    from models.finding import Finding

    result: dict[str, float] = {}

    # Total past vulnerability count for this file
    count_result = await db_session.execute(
        select(func.count(Finding.id)).where(
            Finding.file_path == file_path
        )
    )
    past_vuln_count = count_result.scalar() or 0
    result["past_vuln_count"] = float(past_vuln_count)

    # Days since last vulnerability
    if past_vuln_count > 0:
        from models.scan import Scan

        latest_result = await db_session.execute(
            select(Scan.triggered_at)
            .join(Finding, Finding.scan_id == Scan.id)
            .where(Finding.file_path == file_path)
            .order_by(Scan.triggered_at.desc())
            .limit(1)
        )
        latest_scan_time = latest_result.scalar_one_or_none()

        if latest_scan_time:
            delta = datetime.now(timezone.utc) - latest_scan_time.replace(
                tzinfo=timezone.utc
            ) if latest_scan_time.tzinfo is None else datetime.now(timezone.utc) - latest_scan_time
            result["days_since_last_vuln"] = max(0.0, float(delta.days))
        else:
            result["days_since_last_vuln"] = 9999.0
    else:
        result["days_since_last_vuln"] = 9999.0

    return result


async def _extract_complexity(
    repo_path: str,
    file_path: str,
) -> float:
    """
    Calculate cyclomatic complexity using radon.
    Returns a normalized score between 0.0 and 100.0.
    """
    import os

    full_path = os.path.join(repo_path, file_path)

    if not os.path.exists(full_path):
        return 0.0

    if not file_path.endswith(".py"):
        return 0.0

    try:
        from radon.complexity import cc_visit

        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        blocks = cc_visit(source)

        if not blocks:
            return 0.0

        # Average complexity across all functions/methods
        total_complexity = sum(block.complexity for block in blocks)
        avg_complexity = total_complexity / len(blocks)

        # Normalize to 0-100 scale (complexity of 50+ maps to 100)
        normalized = min(100.0, (avg_complexity / 50.0) * 100.0)

        return round(normalized, 2)

    except (SyntaxError, ImportError, UnicodeDecodeError):
        return 0.0
