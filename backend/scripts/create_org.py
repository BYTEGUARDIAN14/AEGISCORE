"""
AEGISCORE — Organization and Admin User Setup Script
Creates initial organization, default team, and administrator user.
Usage:
    python scripts/create_org.py --org-name "BYTEAEGIS" --admin-email "admin@byteaegis.in" --admin-password "secret123"
"""

import argparse
import asyncio
import os
import re
import sys
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
from models.org import MemberRole, Organization, Team, TeamMembership
from models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text)


async def create_org_and_admin(org_name: str, admin_email: str, admin_password: str, plan: str = "enterprise"):
    """Create organization and admin user."""
    await init_db()

    async with AsyncSessionLocal() as session:
        # 1. Create or get user
        user_result = await session.execute(
            select(User).where(User.email == admin_email.strip().lower())
        )
        user = user_result.scalar_one_or_none()

        if user is None:
            user = User(
                id=uuid4(),
                email=admin_email.strip().lower(),
                hashed_password=pwd_context.hash(admin_password),
                full_name=f"{org_name} Administrator",
                is_active=True,
            )
            session.add(user)
            await session.flush()
            print(f"[+] Created user: {user.email} (ID: {user.id})")
        else:
            # Update password
            user.hashed_password = pwd_context.hash(admin_password)
            user.is_active = True
            await session.flush()
            print(f"[*] User already exists, updated password: {user.email} (ID: {user.id})")

        # 2. Create or get organization
        org_slug = slugify(org_name)
        org_result = await session.execute(
            select(Organization).where(Organization.slug == org_slug)
        )
        org = org_result.scalar_one_or_none()

        if org is None:
            org = Organization(
                id=uuid4(),
                name=org_name,
                slug=org_slug,
                plan=plan,
            )
            session.add(org)
            await session.flush()
            print(f"[+] Created organization: {org.name} (Slug: {org.slug})")
        else:
            print(f"[*] Organization already exists: {org.name} (ID: {org.id})")

        # 3. Create default team if not exists
        team_result = await session.execute(
            select(Team).where(Team.org_id == org.id, Team.slug == "default")
        )
        team = team_result.scalar_one_or_none()

        if team is None:
            team = Team(
                id=uuid4(),
                org_id=org.id,
                name="Security & Engineering",
                slug="default",
            )
            session.add(team)
            await session.flush()
            print(f"[+] Created default team: {team.name}")
        else:
            print(f"[*] Default team exists: {team.name}")

        # 4. Link admin membership
        membership_result = await session.execute(
            select(TeamMembership).where(
                TeamMembership.team_id == team.id,
                TeamMembership.user_id == user.id,
            )
        )
        membership = membership_result.scalar_one_or_none()

        if membership is None:
            membership = TeamMembership(
                id=uuid4(),
                team_id=team.id,
                user_id=user.id,
                role=MemberRole.admin,
            )
            session.add(membership)
            await session.flush()
            print(f"[+] Assigned {user.email} as Admin to team '{team.name}'")
        else:
            membership.role = MemberRole.admin
            print(f"[*] User is already a member with role '{membership.role}'")

        await session.commit()
        print("\n=======================================================")
        print(f"SUCCESS: AEGISCORE initialized for '{org_name}'")
        print(f"Admin Login: {admin_email}")
        print(f"Organization ID: {org.id}")
        print(f"Team ID: {team.id}")
        print("=======================================================\n")


def main():
    parser = argparse.ArgumentParser(description="Initialize AEGISCORE organization and admin user")
    parser.add_argument("--org-name", default="BYTEAEGIS", help="Name of the organization")
    parser.add_argument("--admin-email", default="admin@byteaegis.in", help="Admin email address")
    parser.add_argument("--admin-password", default="admin123", help="Admin password")
    parser.add_argument("--plan", default="enterprise", help="Organization plan tier")

    args = parser.parse_args()
    asyncio.run(create_org_and_admin(args.org_name, args.admin_email, args.admin_password, args.plan))


if __name__ == "__main__":
    main()
