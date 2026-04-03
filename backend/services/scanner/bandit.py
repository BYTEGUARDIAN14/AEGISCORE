"""
AEGISCORE — Bandit Scanner Service
Runs Bandit Python security analysis and normalizes findings.
"""

import asyncio
import json
import os
import uuid
from typing import Any


async def run_bandit(repo_path: str) -> list[dict[str, Any]]:
    """
    Run Bandit security analysis on a Python repository.

    Args:
        repo_path: Absolute path to the cloned repository.

    Returns:
        List of normalized finding dictionaries.
    """
    output_file = f"/tmp/bandit_{uuid.uuid4().hex}.json"
    findings: list[dict[str, Any]] = []

    try:
        # Build command arguments
        cmd_args = [
            "bandit",
            "-r", repo_path,
            "-f", "json",
            "-o", output_file,
            "--quiet",
        ]

        # Execute Bandit as async subprocess
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
            raise TimeoutError("Bandit scan timed out after 300 seconds")

        # Bandit returns exit code 1 when findings are found — this is normal
        # Read output file
        if not os.path.exists(output_file):
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
            severity = _map_severity(result.get("issue_severity", "LOW"))
            confidence = result.get("issue_confidence", "MEDIUM")

            # Extract test ID as rule_id
            rule_id = result.get("test_id", "unknown")
            test_name = result.get("test_name", "")
            if test_name:
                rule_id = f"{rule_id}:{test_name}"

            file_path = result.get("filename", "")
            line_number = result.get("line_number", 0)
            message = result.get("issue_text", "")

            # Extract CWE
            cwe = None
            issue_cwe = result.get("issue_cwe", {})
            if isinstance(issue_cwe, dict):
                cwe_id = issue_cwe.get("id")
                if cwe_id:
                    cwe = f"CWE-{cwe_id}"
            elif isinstance(issue_cwe, str):
                cwe = issue_cwe

            # Make file_path relative to repo_path
            if file_path.startswith(repo_path):
                file_path = file_path[len(repo_path):].lstrip("/").lstrip("\\")

            finding = {
                "scanner": "bandit",
                "severity": severity,
                "rule_id": rule_id,
                "file_path": file_path,
                "line_number": line_number,
                "message": message,
                "cwe": cwe,
                "metadata": {
                    "bandit_severity": result.get("issue_severity", ""),
                    "bandit_confidence": confidence,
                    "test_id": result.get("test_id", ""),
                    "test_name": test_name,
                    "line_range": result.get("line_range", []),
                    "more_info": result.get("more_info", ""),
                    "code": result.get("code", ""),
                },
            }
            findings.append(finding)

    except TimeoutError:
        raise
    except FileNotFoundError:
        raise RuntimeError(
            "Bandit is not installed. Install with: pip install bandit"
        )
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse Bandit output: {e}")
    finally:
        # Clean up temp file
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except OSError:
                pass

    return findings


def _map_severity(bandit_severity: str) -> str:
    """
    Map Bandit severity levels to AEGISCORE severity.

    Mapping:
        HIGH   → HIGH
        MEDIUM → MEDIUM
        LOW    → LOW
    """
    mapping = {
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "LOW": "LOW",
    }
    return mapping.get(bandit_severity.upper(), "LOW")
