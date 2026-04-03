"""
AEGISCORE — Slack Alert Service
Sends critical finding alerts via Slack webhook.
"""

import logging
from typing import Any

import httpx

from config import settings

logger = logging.getLogger("aegiscore.alerts")


async def send_slack_alert(
    findings: list[dict[str, Any]],
    scan: Any,
    repo: Any,
) -> None:
    """
    Send a Slack alert for critical security findings.
    Uses Slack Block Kit for rich formatting.

    Silently returns if SLACK_WEBHOOK_URL is not configured.
    Never raises exceptions — never crashes the scan pipeline.

    Args:
        findings: List of finding dictionaries (critical severity).
        scan: Scan ORM object.
        repo: Repository ORM object.
    """
    if not settings.SLACK_WEBHOOK_URL:
        return

    if not findings:
        return

    try:
        # Filter to alert-worthy findings
        alert_findings = [
            f for f in findings
            if f.get("severity", "").upper() == settings.SLACK_ALERT_SEVERITY.upper()
        ]

        if not alert_findings:
            return

        # Build Slack Block Kit message
        blocks = _build_slack_blocks(alert_findings, scan, repo)

        # Send via webhook
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                settings.SLACK_WEBHOOK_URL,
                json={"blocks": blocks},
            )

            if response.status_code != 200:
                logger.warning(
                    "Slack webhook returned status %d: %s",
                    response.status_code,
                    response.text[:200],
                )

    except httpx.TimeoutException:
        logger.warning("Slack webhook request timed out")
    except httpx.ConnectError:
        logger.warning("Cannot connect to Slack webhook URL")
    except httpx.HTTPError as e:
        logger.warning("HTTP error sending Slack alert: %s", e)
    except Exception as e:
        logger.error("Unexpected error sending Slack alert: %s", e)


def _build_slack_blocks(
    findings: list[dict[str, Any]],
    scan: Any,
    repo: Any,
) -> list[dict[str, Any]]:
    """Build Slack Block Kit blocks for the alert message."""
    commit_sha = getattr(scan, "commit_sha", "unknown")[:8]
    branch = getattr(scan, "branch", "unknown")
    repo_name = getattr(repo, "name", "unknown")
    scan_time = getattr(scan, "triggered_at", "unknown")

    if hasattr(scan_time, "strftime"):
        scan_time = scan_time.strftime("%Y-%m-%d %H:%M UTC")

    blocks: list[dict[str, Any]] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":shield: [AEGISCORE] Critical Security Alert",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Repository:*\n{repo_name}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Branch:*\n{branch}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Commit:*\n`{commit_sha}`",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Scan Time:*\n{scan_time}",
                },
            ],
        },
        {
            "type": "divider",
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":rotating_light: *{len(findings)} Critical Finding(s) Detected*",
            },
        },
    ]

    # Add finding details (max 10 to avoid message size limit)
    for finding in findings[:10]:
        severity = finding.get("severity", "UNKNOWN")
        rule_id = finding.get("rule_id", "unknown")
        file_path = finding.get("file_path", "unknown")
        line_number = finding.get("line_number", 0)
        message = finding.get("message", "No description")

        # Truncate message
        if len(message) > 120:
            message = message[:117] + "..."

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*{severity}* — `{rule_id}`\n"
                    f"`{file_path}:{line_number}`\n"
                    f"{message}"
                ),
            },
        })

    if len(findings) > 10:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"_...and {len(findings) - 10} more findings._",
            },
        })

    # Footer
    blocks.extend([
        {
            "type": "divider",
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": (
                        ":link: View full report in AEGISCORE dashboard | "
                        "Powered by BYTEAEGIS"
                    ),
                },
            ],
        },
    ])

    return blocks
