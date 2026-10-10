"""
AEGISCORE — Comprehensive Demo Data Seeder
Populates database with complete realistic organizations, teams, repositories,
scans, security findings, cross-repo correlations, risk scores, and AI fixes.
Also trains and saves an initial risk forecasting model.
Usage:
    python scripts/seed_demo_data.py
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

# Ensure backend root is in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from passlib.context import CryptContext
from sqlalchemy import select

from config import settings
from database import AsyncSessionLocal, init_db
from models.finding import CrossRepoLink, Finding, Severity
from models.fix import FixConfidence, FixSuggestion
from models.org import MemberRole, Organization, Team, TeamMembership
from models.repo import Repository
from models.risk import RiskHistory, RiskScore
from models.scan import Scan, ScanStatus, ScanTask, ScannerType
from models.user import User
from services.ai.risk_model import RiskModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed():
    print("[*] Initializing database schema...")
    await init_db()

    async with AsyncSessionLocal() as session:
        # 1. Admin & Developer Users
        users_data = [
            ("admin@byteaegis.in", "admin123", "Mohamed Adhnaan (Admin)"),
            ("alice@byteaegis.in", "alice123", "Alice Chen (SecLead)"),
            ("bob@byteaegis.in", "bob123", "Bob Martinez (Dev)"),
        ]
        created_users = {}
        for email, password, full_name in users_data:
            res = await session.execute(select(User).where(User.email == email))
            u = res.scalar_one_or_none()
            if not u:
                u = User(
                    id=uuid4(),
                    email=email,
                    hashed_password=pwd_context.hash(password),
                    full_name=full_name,
                    is_active=True,
                )
                session.add(u)
                await session.flush()
            created_users[email] = u

        admin_user = created_users["admin@byteaegis.in"]
        print(f"[+] Verified {len(created_users)} users.")

        # 2. Organization
        res = await session.execute(select(Organization).where(Organization.slug == "byteaegis"))
        org = res.scalar_one_or_none()
        if not org:
            org = Organization(
                id=uuid4(),
                name="BYTEAEGIS",
                slug="byteaegis",
                plan="enterprise",
                scan_count=42,
            )
            session.add(org)
            await session.flush()
        print(f"[+] Verified Organization: {org.name}")

        # 3. Teams
        teams_data = [
            ("Team Alfa", "alfa"),
            ("Team Beta", "beta"),
            ("Team Gamma", "gamma"),
        ]
        created_teams = {}
        for name, slug in teams_data:
            res = await session.execute(
                select(Team).where(Team.org_id == org.id, Team.slug == slug)
            )
            t = res.scalar_one_or_none()
            if not t:
                t = Team(id=uuid4(), org_id=org.id, name=name, slug=slug)
                session.add(t)
                await session.flush()
            created_teams[slug] = t

            # Add memberships
            res_m = await session.execute(
                select(TeamMembership).where(TeamMembership.team_id == t.id, TeamMembership.user_id == admin_user.id)
            )
            if not res_m.scalar_one_or_none():
                session.add(TeamMembership(id=uuid4(), team_id=t.id, user_id=admin_user.id, role=MemberRole.admin))
        await session.flush()
        print(f"[+] Verified {len(created_teams)} teams.")

        # 4. Repositories
        repos_data = [
            ("api-gateway", "https://github.com/BYTEGUARDIAN14/api-gateway", created_teams["alfa"].id),
            ("auth-service", "https://github.com/BYTEGUARDIAN14/auth-service", created_teams["alfa"].id),
            ("payment-portal", "https://github.com/BYTEGUARDIAN14/payment-portal", created_teams["beta"].id),
            ("core-infra", "https://github.com/BYTEGUARDIAN14/core-infra", created_teams["gamma"].id),
        ]
        created_repos = {}
        for name, url, team_id in repos_data:
            res = await session.execute(select(Repository).where(Repository.name == name))
            r = res.scalar_one_or_none()
            if not r:
                r = Repository(
                    id=uuid4(),
                    team_id=team_id,
                    name=name,
                    github_url=url,
                    default_branch="main",
                    is_active=True,
                    last_scan_at=datetime.now(timezone.utc) - timedelta(minutes=15),
                )
                session.add(r)
                await session.flush()
            created_repos[name] = r
        print(f"[+] Verified {len(created_repos)} repositories.")

        # 5. Scans & ScanTasks
        created_scans = {}
        for r_name, r in created_repos.items():
            res = await session.execute(select(Scan).where(Scan.repo_id == r.id))
            scan = res.scalar_one_or_none()
            if not scan:
                scan = Scan(
                    id=uuid4(),
                    repo_id=r.id,
                    commit_sha="a3f9d12e8b7c4d5e6f1a2b3c4d5e6f7a8b9c0d1e",
                    branch="main",
                    triggered_at=datetime.now(timezone.utc) - timedelta(minutes=30),
                    completed_at=datetime.now(timezone.utc) - timedelta(minutes=28),
                    status=ScanStatus.completed,
                    total_findings=5,
                    critical_count=1,
                    high_count=2,
                    medium_count=1,
                    low_count=1,
                    duration_ms=45200,
                )
                session.add(scan)
                await session.flush()

                # Add tasks
                for s_type in [ScannerType.semgrep, ScannerType.bandit, ScannerType.trivy]:
                    session.add(ScanTask(
                        id=uuid4(),
                        scan_id=scan.id,
                        scanner=s_type,
                        status=ScanStatus.completed,
                        started_at=scan.triggered_at,
                        completed_at=scan.completed_at,
                        findings_count=2,
                    ))
            created_scans[r_name] = scan
        await session.flush()

        # 6. Realistic Findings
        shared_rule_pw = "python.lang.security.audit.hardcoded-password"
        shared_rule_xxe = "python.lang.security.audit.use-defused-xml"

        findings_blueprint = [
            # api-gateway
            ("api-gateway", "semgrep", Severity.CRITICAL, shared_rule_pw, "app/config/settings.py", 22,
             "Hardcoded database credential detected in configuration dictionary.", "CWE-798"),
            ("api-gateway", "semgrep", Severity.HIGH, shared_rule_xxe, "app/parsers/xml_handler.py", 34,
             "Standard xml.etree.ElementTree vulnerable to XXE external entity resolution.", "CWE-611"),
            ("api-gateway", "bandit", Severity.HIGH, "B608:hardcoded_sql_expressions", "app/db/query.py", 45,
             "Possible SQL injection vector via raw string formatting.", "CWE-89"),
            ("api-gateway", "trivy", Severity.MEDIUM, "CVE-2023-44487", "requirements.txt", 12,
             "HTTP/2 Rapid Reset attack vector in underlying transport dependency.", "CWE-400"),

            # auth-service (shares the hardcoded pw rule & xxe rule for cross-repo correlation!)
            ("auth-service", "semgrep", Severity.CRITICAL, shared_rule_pw, "src/auth/jwt_keys.py", 18,
             "Hardcoded default JWT signing secret found in auth initialization.", "CWE-798"),
            ("auth-service", "bandit", Severity.HIGH, "B301:pickle", "src/auth/session.py", 62,
             "Insecure deserialization using pickle.loads on client cookie data.", "CWE-502"),
            ("auth-service", "semgrep", Severity.HIGH, shared_rule_xxe, "src/saml/parser.py", 29,
             "SAML metadata parser uses vulnerable XML engine without entity expansion disabled.", "CWE-611"),

            # payment-portal
            ("payment-portal", "semgrep", Severity.CRITICAL, "javascript.express.security.audit.cors", "routes/checkout.js", 15,
             "Wildcard CORS Access-Control-Allow-Origin: * on authenticated credit card checkout route.", "CWE-942"),
            ("payment-portal", "semgrep", Severity.HIGH, "javascript.lang.security.detect-child-process", "services/receipt.js", 41,
             "Direct user input passed to child_process.exec without validation.", "CWE-78"),
        ]

        created_findings = []
        for r_name, scanner, sev, rule, file_p, line_no, msg, cwe in findings_blueprint:
            scan = created_scans[r_name]
            res_f = await session.execute(
                select(Finding).where(Finding.scan_id == scan.id, Finding.file_path == file_p)
            )
            finding = res_f.scalar_one_or_none()
            if not finding:
                finding = Finding(
                    id=uuid4(),
                    scan_id=scan.id,
                    scanner=scanner,
                    severity=sev,
                    rule_id=rule,
                    file_path=file_p,
                    line_number=line_no,
                    message=msg,
                    cwe=cwe,
                    metadata_={"tags": ["owasp-top-10", "security-audit"]},
                )
                session.add(finding)
                await session.flush()
            created_findings.append(finding)

        print(f"[+] Verified {len(created_findings)} security findings.")

        # 7. Cross-Repo Links (Correlate findings that share rule_ids)
        for i in range(len(created_findings)):
            for j in range(i + 1, len(created_findings)):
                f1 = created_findings[i]
                f2 = created_findings[j]
                if f1.rule_id == f2.rule_id and f1.scan_id != f2.scan_id:
                    res_c = await session.execute(
                        select(CrossRepoLink).where(
                            (CrossRepoLink.finding_id_a == f1.id) & (CrossRepoLink.finding_id_b == f2.id)
                        )
                    )
                    if not res_c.scalar_one_or_none():
                        session.add(CrossRepoLink(
                            id=uuid4(),
                            finding_id_a=f1.id,
                            finding_id_b=f2.id,
                            correlation_type="same_rule",
                        ))
        await session.flush()
        print("[+] Verified cross-repo correlation links.")

        # 8. Fix Suggestions (Unified diffs)
        for f in created_findings:
            if f.severity in (Severity.CRITICAL, Severity.HIGH):
                res_fix = await session.execute(
                    select(FixSuggestion).where(FixSuggestion.finding_id == f.id)
                )
                if not res_fix.scalar_one_or_none():
                    diff = f"""--- a/{f.file_path}
+++ b/{f.file_path}
@@ -{max(1, f.line_number - 2)},5 +{max(1, f.line_number - 2)},5 @@
-    # INSECURE: {f.message}
-    SECRET_KEY = "hardcoded-secret-123"
+    # SECURE FIX: Load securely from environment
+    import os
+    SECRET_KEY = os.environ.get("AEGISCORE_SECRET_KEY")
+    if not SECRET_KEY:
+        raise RuntimeError("AEGISCORE_SECRET_KEY must be provided")"""
                    explanation = (
                        f"Remediates {f.rule_id} ({f.cwe}). Replaces hardcoded values with "
                        "environment variable injection and runtime validation."
                    )
                    session.add(FixSuggestion(
                        id=uuid4(),
                        finding_id=f.id,
                        model_used="codellama:7b",
                        unified_diff=diff,
                        explanation=explanation,
                        confidence=FixConfidence.high,
                        applied=False,
                    ))
        await session.flush()
        print("[+] Verified AI fix suggestions.")

        # 9. Risk Scores & History
        sample_files = [
            ("app/auth/views.py", 0.92),
            ("app/api/serializers.py", 0.74),
            ("app/utils/crypto.py", 0.61),
            ("app/models/user.py", 0.38),
            ("app/config/settings.py", 0.88),
            ("routes/checkout.js", 0.95),
            ("src/auth/jwt_keys.py", 0.89),
        ]
        api_repo = created_repos["api-gateway"]
        for f_path, score in sample_files:
            res_rs = await session.execute(
                select(RiskScore).where(RiskScore.repo_id == api_repo.id, RiskScore.file_path == f_path)
            )
            rs = res_rs.scalar_one_or_none()
            if not rs:
                snapshot = {
                    "commit_frequency_30d": 18.0 if score > 0.7 else 3.0,
                    "author_count": 5.0,
                    "avg_diff_size": 120.0,
                    "past_vuln_count": 3.0 if score > 0.7 else 0.0,
                    "days_since_last_vuln": 4.0 if score > 0.7 else 180.0,
                    "file_complexity_score": 42.0,
                    "import_risk_score": 0.8,
                    "test_coverage_ratio": 0.35,
                }
                rs = RiskScore(
                    id=uuid4(),
                    repo_id=api_repo.id,
                    file_path=f_path,
                    score=score,
                    model_version="v2026.1",
                    feature_snapshot=snapshot,
                )
                session.add(rs)

                # Add historical trend points
                for days_ago in [25, 18, 10, 2]:
                    session.add(RiskHistory(
                        id=uuid4(),
                        repo_id=api_repo.id,
                        file_path=f_path,
                        score=max(0.1, min(1.0, score + (days_ago * 0.01) - 0.1)),
                        recorded_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
                    ))
        await session.commit()
        print("[+] Verified Risk scores and history.")

    # 10. Train initial RiskModel and save artifact
    print("[*] Training initial Random Forest Risk Model...")
    os.makedirs(os.path.dirname(settings.ML_MODEL_PATH), exist_ok=True)
    model = RiskModel(settings.ML_MODEL_PATH)
    
    # Generate balanced synthetic training samples based on the feature space
    training_samples = []
    for i in range(80):
        is_risky = (i % 2 == 0)
        training_samples.append({
            "commit_frequency_30d": 25.0 if is_risky else 2.0,
            "author_count": 6.0 if is_risky else 1.0,
            "avg_diff_size": 180.0 if is_risky else 20.0,
            "past_vuln_count": 4.0 if is_risky else 0.0,
            "days_since_last_vuln": 2.0 if is_risky else 365.0,
            "file_complexity_score": 65.0 if is_risky else 12.0,
            "import_risk_score": 0.85 if is_risky else 0.15,
            "test_coverage_ratio": 0.20 if is_risky else 0.85,
            "had_vuln_next_scan": is_risky,
        })
    metrics = model.train(training_samples)
    print(f"[+] Risk Model trained and saved to {settings.ML_MODEL_PATH} (F1: {metrics['f1_score']:.3f}, Precision: {metrics['precision']:.3f}, Recall: {metrics['recall']:.3f})")

    print("\n=======================================================")
    print("SUCCESS: Full demo environment seeded successfully!")
    print("Login with: admin@byteaegis.in / admin123")
    print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(seed())
