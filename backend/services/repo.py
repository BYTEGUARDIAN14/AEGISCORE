"""
AEGISCORE — Repository Service
Handles cloning and updating local copies of repositories for scanning.
"""

import os
import shutil
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger("aegiscore.services.repo")

async def clone_repository(github_url: str, repo_path: str, branch: str = "main") -> str:
    """
    Clone a GitHub repository to a local path.
    If the path exists, it will be removed and re-cloned to ensure a clean state.
    """
    try:
        # Create parent directory if it doesn't exist
        parent_dir = Path(repo_path).parent
        parent_dir.mkdir(parents=True, exist_ok=True)

        # Remove existing directory if it exists
        if os.path.exists(repo_path):
            logger.info(f"Removing existing repo at {repo_path}")
            shutil.rmtree(repo_path)

        # Build git clone command
        cmd = [
            "git", "clone",
            "--depth", "1",
            "--branch", branch,
            github_url,
            repo_path
        ]

        logger.info(f"Cloning {github_url} (branch: {branch}) to {repo_path}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
        
        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            logger.error(f"Git clone failed: {error_msg}")
            raise RuntimeError(f"Failed to clone repository: {error_msg}")

        logger.info(f"Successfully cloned repository to {repo_path}")
        return repo_path

    except asyncio.TimeoutError:
        logger.error("Git clone timed out")
        raise TimeoutError("Repository cloning timed out after 120 seconds")
    except Exception as e:
        logger.error(f"Error during repository cloning: {e}")
        raise
