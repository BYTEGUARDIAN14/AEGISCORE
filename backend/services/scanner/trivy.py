"""
AEGISCORE — Trivy Scanner Service
Runs Trivy SCA/container vulnerability analysis and normalizes findings.
"""

import asyncio
import json
import os
import uuid
from typing import Any


async def run_trivy(repo_path: str) -> list[dict[str, Any]]:
    """
    Run Trivy filesystem security analysis on a repository.
    Scans for dependency and container vulnerabilities.

    Args:
        repo_path: Absolute path to the cloned repository.

    Returns:
        List of normalized finding dictionaries.
    """
    output_file = f"/tmp/trivy_{uuid.uuid4().hex}.json"
    findings: list[dict[str, Any]] = []

    try:
        # Build command arguments
        cmd_args = [
            "trivy",
            "fs",
            "--format", "json",
            "--output", output_file,
            "--quiet",
            repo_path,
        ]

        # Execute Trivy as async subprocess
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
            raise TimeoutError("Trivy scan timed out after 300 seconds")

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

        # Parse results — Trivy nests vulnerabilities under Results
        results = data.get("Results", [])

        for result_block in results:
            target = result_block.get("Target", "")
            result_type = result_block.get("Type", "")
            vulnerabilities = result_block.get("Vulnerabilities", [])

            if vulnerabilities is None:
                continue

            for vuln in vulnerabilities:
                severity = _map_severity(vuln.get("Severity", "UNKNOWN"))
                vuln_id = vuln.get("VulnerabilityID", "unknown")
                pkg_name = vuln.get("PkgName", "")
                installed_version = vuln.get("InstalledVersion", "")
                fixed_version = vuln.get("FixedVersion", "")
                title = vuln.get("Title", "")
                description = vuln.get("Description", "")

                # Build message
                message_parts = []
                if title:
                    message_parts.append(title)
                if pkg_name:
                    version_info = f"{pkg_name}@{installed_version}"
                    if fixed_version:
                        version_info += f" (fix: {fixed_version})"
                    message_parts.append(version_info)
                if not message_parts and description:
                    message_parts.append(description[:200])

                message = " — ".join(message_parts) if message_parts else vuln_id

                # Extract CWE IDs
                cwe = None
                cwe_ids = vuln.get("CweIDs", [])
                if isinstance(cwe_ids, list) and cwe_ids:
                    cwe = str(cwe_ids[0])

                # Make target relative
                file_path = target
                if file_path.startswith(repo_path):
                    file_path = file_path[len(repo_path):].lstrip("/").lstrip("\\")

                finding = {
                    "scanner": "trivy",
                    "severity": severity,
                    "rule_id": vuln_id,
                    "file_path": file_path,
                    "line_number": 0,
                    "message": message,
                    "cwe": cwe,
                    "metadata": {
                        "vulnerability_id": vuln_id,
                        "pkg_name": pkg_name,
                        "installed_version": installed_version,
                        "fixed_version": fixed_version,
                        "type": result_type,
                        "title": title,
                        "description": description[:500] if description else "",
                        "references": vuln.get("References", [])[:5],
                        "data_source": vuln.get("DataSource", {}),
                        "primary_url": vuln.get("PrimaryURL", ""),
                    },
                }
                findings.append(finding)

    except TimeoutError:
        raise
    except FileNotFoundError:
        raise RuntimeError(
            "Trivy is not installed. "
            "Install from: https://aquasecurity.github.io/trivy/"
        )
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse Trivy output: {e}")
    finally:
        # Clean up temp file
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except OSError:
                pass

    return findings


def _map_severity(trivy_severity: str) -> str:
    """
    Map Trivy severity levels to AEGISCORE severity.
    Trivy already uses CRITICAL/HIGH/MEDIUM/LOW — direct mapping.
    """
    mapping = {
        "CRITICAL": "CRITICAL",
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "LOW": "LOW",
        "UNKNOWN": "LOW",
    }
    return mapping.get(trivy_severity.upper(), "LOW")
