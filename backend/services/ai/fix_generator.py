"""
AEGISCORE — Fix Generator Service
Generates AI-powered code fixes via local Ollama LLM.
Zero data egress — fully air-gap compatible.
"""

import logging
import re
from typing import Any

import httpx

from config import settings

logger = logging.getLogger("aegiscore.fix_generator")


async def generate_fix(
    finding: dict[str, Any],
    code_context: str,
) -> dict[str, Any] | None:
    """
    Generate an AI-powered code fix for a security finding.
    Uses local Ollama instance (codellama:7b) with zero data egress.

    Args:
        finding: Dictionary containing:
            - severity, rule_id, file_path, line_number, message, cwe
        code_context: Source code surrounding the vulnerable line
            (10 lines before + flagged lines + 10 lines after)

    Returns:
        Dictionary with unified_diff, explanation, confidence, model_used.
        Returns None if generation fails for any reason.
    """
    try:
        # Detect language from file extension
        file_path = finding.get("file_path", "")
        language = _detect_language(file_path)

        # Build structured prompt
        prompt = _build_prompt(finding, code_context, language)

        # Call Ollama API
        ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"

        async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
            response = await client.post(
                ollama_url,
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 512,
                    },
                },
            )

            if response.status_code != 200:
                logger.warning(
                    "Ollama returned status %d: %s",
                    response.status_code,
                    response.text[:200],
                )
                return None

            data = response.json()
            generated_text = data.get("response", "")

        if not generated_text.strip():
            logger.warning("Ollama returned empty response")
            return None

        # Parse the generated response
        unified_diff = _extract_diff(generated_text)
        explanation = _extract_explanation(generated_text)
        confidence = _determine_confidence(unified_diff, explanation)

        if not unified_diff:
            logger.warning("No valid diff found in Ollama response")
            return None

        return {
            "unified_diff": unified_diff,
            "explanation": explanation,
            "confidence": confidence,
            "model_used": settings.OLLAMA_MODEL,
        }

    except httpx.TimeoutException:
        logger.warning(
            "Ollama request timed out after %ds for %s",
            settings.OLLAMA_TIMEOUT,
            finding.get("file_path", "unknown"),
        )
        return None
    except httpx.ConnectError:
        logger.warning(
            "Cannot connect to Ollama at %s. Is it running?",
            settings.OLLAMA_BASE_URL,
        )
        return None
    except httpx.HTTPError as e:
        logger.warning("HTTP error calling Ollama: %s", e)
        return None
    except (KeyError, ValueError, TypeError) as e:
        logger.warning("Failed to parse Ollama response: %s", e)
        return None
    except Exception as e:
        logger.error(
            "Unexpected error generating fix for %s: %s",
            finding.get("file_path", "unknown"),
            e,
        )
        return None


def _build_prompt(
    finding: dict[str, Any],
    code_context: str,
    language: str,
) -> str:
    """Build a structured prompt for the LLM."""
    severity = finding.get("severity", "UNKNOWN")
    rule_id = finding.get("rule_id", "unknown")
    file_path = finding.get("file_path", "")
    line_number = finding.get("line_number", 0)
    message = finding.get("message", "")
    cwe = finding.get("cwe", "")

    cwe_section = f"\nCWE: {cwe}" if cwe else ""

    return f"""You are a security engineer fixing a vulnerability in production code.

VULNERABILITY DETAILS:
  Severity: {severity}
  Rule ID: {rule_id}
  File: {file_path}
  Line: {line_number}
  Language: {language}{cwe_section}

SCANNER MESSAGE:
  {message}

VULNERABLE CODE:
```{language}
{code_context}
```

INSTRUCTIONS:
1. Provide a unified diff that fixes ONLY the security vulnerability.
2. Do not change functionality, style, or unrelated code.
3. Output the diff first, then a brief explanation.
4. The diff must use standard unified diff format (--- / +++ / @@ / + / - prefixes).

UNIFIED DIFF:
"""


def _extract_diff(text: str) -> str:
    """
    Extract unified diff section from generated text.
    Looks for lines starting with ---, +++, @@, +, or -.
    """
    lines = text.split("\n")
    diff_lines = []
    in_diff = False

    for line in lines:
        stripped = line.rstrip()

        # Detect start of diff
        if stripped.startswith("---") or stripped.startswith("+++"):
            in_diff = True
            diff_lines.append(stripped)
            continue

        if stripped.startswith("@@"):
            in_diff = True
            diff_lines.append(stripped)
            continue

        if in_diff:
            if (
                stripped.startswith("+")
                or stripped.startswith("-")
                or stripped.startswith(" ")
                or stripped == ""
            ):
                diff_lines.append(stripped)
            elif stripped.startswith("```"):
                # End of code block
                break
            else:
                # Check if this is explanation text
                if not any(
                    stripped.startswith(p)
                    for p in ["diff", "---", "+++", "@@", "+", "-", " "]
                ):
                    break
                diff_lines.append(stripped)

    # Also try to extract from code blocks
    if not diff_lines:
        code_block_pattern = r"```(?:diff)?\s*\n(.*?)```"
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        for match in matches:
            candidate_lines = match.strip().split("\n")
            has_diff_markers = any(
                l.startswith("---") or l.startswith("+++") or l.startswith("@@")
                for l in candidate_lines
            )
            if has_diff_markers:
                diff_lines = candidate_lines
                break

    return "\n".join(diff_lines).strip()


def _extract_explanation(text: str) -> str:
    """
    Extract the explanation text from the generated response.
    Everything after the diff section is considered explanation.
    """
    lines = text.split("\n")
    explanation_lines = []
    past_diff = False
    blank_count = 0

    for line in lines:
        stripped = line.strip()

        if past_diff:
            explanation_lines.append(line)
        elif stripped.startswith(("Explanation", "EXPLANATION", "Fix explanation")):
            past_diff = True
            continue
        elif any(
            stripped.startswith(p) for p in ["---", "+++", "@@", "+", "-"]
        ):
            continue
        elif stripped.startswith("```"):
            if past_diff:
                continue
            past_diff = True
            continue

    explanation = "\n".join(explanation_lines).strip()

    # If no explanation found, use the last paragraph
    if not explanation:
        paragraphs = text.split("\n\n")
        if len(paragraphs) > 1:
            explanation = paragraphs[-1].strip()
        else:
            explanation = "Fix applied based on security best practices."

    # Clean up code block markers
    explanation = explanation.replace("```", "").strip()

    return explanation


def _determine_confidence(diff: str, explanation: str) -> str:
    """
    Determine confidence level of the generated fix.

    HIGH:   Clean, parseable diff with proper markers
    MEDIUM: Partial diff or missing some markers
    LOW:    Unclear or unparseable output
    """
    if not diff:
        return "low"

    has_file_markers = "---" in diff and "+++" in diff
    has_hunk_header = "@@" in diff
    has_additions = any(
        line.startswith("+") and not line.startswith("+++")
        for line in diff.split("\n")
    )
    has_removals = any(
        line.startswith("-") and not line.startswith("---")
        for line in diff.split("\n")
    )

    score = sum([
        has_file_markers,
        has_hunk_header,
        has_additions,
        has_removals,
        len(explanation) > 20,
    ])

    if score >= 4:
        return "high"
    elif score >= 2:
        return "medium"
    else:
        return "low"


def _detect_language(file_path: str) -> str:
    """Detect programming language from file extension."""
    extension_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".r": "r",
        ".sh": "bash",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".json": "json",
        ".xml": "xml",
        ".sql": "sql",
        ".html": "html",
        ".css": "css",
    }

    for ext, lang in extension_map.items():
        if file_path.lower().endswith(ext):
            return lang

    return "text"
