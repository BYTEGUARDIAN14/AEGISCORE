"""
AEGISCORE — Cross-Repository Correlation Service
Detects propagated vulnerabilities across repositories in the same org.
"""

import logging
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.finding import CrossRepoLink, Finding
from models.org import Team
from models.repo import Repository
from models.scan import Scan

logger = logging.getLogger("aegiscore.correlation")


async def run_correlation(
    scan_id: UUID,
    db: AsyncSession,
) -> int:
    """
    Correlate findings from a completed scan with findings in other
    repositories within the same organization.

    For each finding, searches for other findings with the same rule_id
    in different repos of the same org. Creates CrossRepoLink records
    for each match (if not already linked).

    Args:
        scan_id: UUID of the completed scan.
        db: Async database session.

    Returns:
        Count of new correlations found.
    """
    new_correlations = 0

    # Load scan and its findings
    scan_result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = scan_result.scalar_one_or_none()
    if scan is None:
        logger.warning("Scan %s not found for correlation", scan_id)
        return 0

    # Get the repository and its organization
    repo_result = await db.execute(
        select(Repository).where(Repository.id == scan.repo_id)
    )
    repo = repo_result.scalar_one_or_none()
    if repo is None:
        logger.warning("Repository not found for scan %s", scan_id)
        return 0

    team_result = await db.execute(
        select(Team).where(Team.id == repo.team_id)
    )
    team = team_result.scalar_one_or_none()
    if team is None:
        logger.warning("Team not found for repo %s", repo.id)
        return 0

    org_id = team.org_id

    # Get all repo IDs in the same org (excluding current repo)
    org_repos_result = await db.execute(
        select(Repository.id)
        .join(Team, Repository.team_id == Team.id)
        .where(
            Team.org_id == org_id,
            Repository.id != repo.id,
            Repository.is_active == True,
        )
    )
    other_repo_ids = [row[0] for row in org_repos_result.all()]

    if not other_repo_ids:
        logger.info(
            "No other repos in org for correlation (scan %s)", scan_id
        )
        return 0

    # Load findings for this scan
    findings_result = await db.execute(
        select(Finding).where(Finding.scan_id == scan_id)
    )
    scan_findings = findings_result.scalars().all()

    if not scan_findings:
        return 0

    # Get unique rule_ids from this scan
    rule_ids = set(f.rule_id for f in scan_findings)

    # Find matching findings in other repos
    for rule_id in rule_ids:
        # Findings from this scan with this rule
        current_findings = [f for f in scan_findings if f.rule_id == rule_id]

        # Findings from other repos with the same rule
        other_findings_result = await db.execute(
            select(Finding)
            .join(Scan, Finding.scan_id == Scan.id)
            .where(
                Finding.rule_id == rule_id,
                Scan.repo_id.in_(other_repo_ids),
            )
        )
        other_findings = other_findings_result.scalars().all()

        if not other_findings:
            continue

        # Create links between findings (avoid duplicates)
        for current_finding in current_findings:
            for other_finding in other_findings:
                # Check if link already exists (in either direction)
                existing = await db.execute(
                    select(CrossRepoLink).where(
                        (
                            (CrossRepoLink.finding_id_a == current_finding.id)
                            & (CrossRepoLink.finding_id_b == other_finding.id)
                        )
                        | (
                            (CrossRepoLink.finding_id_a == other_finding.id)
                            & (CrossRepoLink.finding_id_b == current_finding.id)
                        )
                    )
                )

                if existing.scalar_one_or_none() is not None:
                    continue

                # Create new correlation link
                link = CrossRepoLink(
                    finding_id_a=current_finding.id,
                    finding_id_b=other_finding.id,
                    correlation_type="same_rule",
                )
                db.add(link)
                new_correlations += 1

    if new_correlations > 0:
        await db.commit()
        logger.info(
            "Found %d new cross-repo correlations for scan %s",
            new_correlations,
            scan_id,
        )

    return new_correlations
