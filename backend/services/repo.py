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
    Clone a repository to a local path.
    Supports remote GitHub/Git URLs as well as local directories.
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

        # 1. Handle local directory paths
        if os.path.isdir(github_url):
            logger.info(f"Cloning from local directory: {github_url} -> {repo_path}")
            git_dir = os.path.join(github_url, ".git")
            if os.path.exists(git_dir):
                # Try git clone locally
                cmd = ["git", "clone", "--depth", "1", github_url, repo_path]
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
                if process.returncode == 0:
                    logger.info(f"Successfully cloned local repo to {repo_path}")
                    return repo_path

            # Fallback: copy tree directly
            shutil.copytree(
                github_url,
                repo_path,
                ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"),
            )
            logger.info(f"Successfully copied local directory to {repo_path}")
            return repo_path

        # 2. Remote git clone with specified branch
        cmd = [
            "git", "clone",
            "--depth", "1",
            "--branch", branch,
            github_url,
            repo_path,
        ]

        logger.info(f"Cloning {github_url} (branch: {branch}) to {repo_path}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=180)
        
        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            logger.warning(f"Git clone with branch '{branch}' failed: {error_msg}. Retrying default branch...")
            
            # Clean up partial directory if created
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)

            # Retry without explicit branch (clone default branch)
            cmd_fallback = [
                "git", "clone",
                "--depth", "1",
                github_url,
                repo_path,
            ]
            process_fallback = await asyncio.create_subprocess_exec(
                *cmd_fallback,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout_fb, stderr_fb = await asyncio.wait_for(process_fallback.communicate(), timeout=180)
            
            if process_fallback.returncode != 0:
                fb_error = stderr_fb.decode().strip()
                logger.error(f"Fallback git clone failed: {fb_error}")
                raise RuntimeError(f"Failed to clone repository: {fb_error}")

        logger.info(f"Successfully cloned repository to {repo_path}")
        return repo_path

    except asyncio.TimeoutError:
        logger.error("Git clone timed out")
        raise TimeoutError("Repository cloning timed out after 180 seconds")
    except Exception as e:
        logger.error(f"Error during repository cloning: {e}")
        raise
