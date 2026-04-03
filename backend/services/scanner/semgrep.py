"""
AEGISCORE — Semgrep Scanner Service
Runs Semgrep SAST analysis and normalizes findings.
"""

import asyncio
import json
import os
import uuid
from pathlib import Path
from typing import Any

from config import settings


async def run_semgrep(repo_path: str, rules: str) -> list[dict[str, Any]]:
    """
    Run Semgrep security analysis on a repository.

    Args:
        repo_path: Absolute path to the cloned repository.
        rules: Semgrep rule configuration string (e.g., 'p/owasp-top-ten').

    Returns:
        List of normalized finding dictionaries.
    """
    output_file = f"/tmp/sg_{uuid.uuid4().hex}.json"
    findings: list[dict[str, Any]] = []

    try:
        # Build command arguments
        cmd_args = [
            "semgrep",
            "--config", rules,
            "--json",
            "--output", output_file,
            "--no-git-ignore",
            "--quiet",
            repo_path,
        ]

        # Execute Semgrep as async subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300,
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            raise TimeoutError("Semgrep scan timed out after 300 seconds")

        # Read output file
        if not os.path.exists(output_file):
            # Semgrep may write to stdout if output file fails
            if stdout:
                try:
                    data = json.loads(stdout.decode("utf-8"))
                except json.JSONDecodeError:
                    return findings
            else:
                return findings
        else:
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)

        # Parse results
        results = data.get("results", [])

        for result in results:
            severity = _map_severity(result.get("extra", {}).get("severity", "INFO"))
            rule_id = result.get("check_id", "unknown")
            file_path = result.get("path", "")
            line_number = result.get("start", {}).get("line", 0)
            message = result.get("extra", {}).get("message", "")

            # Extract CWE from metadata if available
            cwe = None
            metadata = result.get("extra", {}).get("metadata", {})
            if isinstance(metadata, dict):
                cwe_list = metadata.get("cwe", [])
                if isinstance(cwe_list, list) and cwe_list:
                    cwe = str(cwe_list[0])
                elif isinstance(cwe_list, str):
                    cwe = cwe_list

            # Make file_path relative to repo_path
            if file_path.startswith(repo_path):
                file_path = file_path[len(repo_path):].lstrip("/").lstrip("\\")

            finding = {
                "scanner": "semgrep",
                "severity": severity,
                "rule_id": rule_id,
                "file_path": file_path,
                "line_number": line_number,
                "message": message,
                "cwe": cwe,
                "metadata": {
                    "semgrep_severity": result.get("extra", {}).get("severity", ""),
                    "fingerprint": result.get("extra", {}).get("fingerprint", ""),
                    "lines": result.get("extra", {}).get("lines", ""),
                    "fix": result.get("extra", {}).get("fix", ""),
                },
            }
            findings.append(finding)

    except TimeoutError:
        raise
    except FileNotFoundError:
        raise RuntimeError(
            "Semgrep is not installed. Install with: pip install semgrep"
        )
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse Semgrep output: {e}")
    finally:
        # Clean up temp file
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except OSError:
                pass

    return findings


def _map_severity(semgrep_severity: str) -> str:
    """
    Map Semgrep severity levels to AEGISCORE severity.

    Mapping:
        ERROR   → CRITICAL
        WARNING → HIGH
        INFO    → MEDIUM
        *       → LOW
    """
    mapping = {
        "ERROR": "CRITICAL",
        "WARNING": "HIGH",
        "INFO": "MEDIUM",
    }
    return mapping.get(semgrep_severity.upper(), "LOW")
