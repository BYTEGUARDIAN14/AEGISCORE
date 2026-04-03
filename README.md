<div align="center">

<br/>

```
 █████╗ ███████╗ ██████╗ ██╗███████╗ ██████╗ ██████╗ ██████╗ ███████╗
██╔══██╗██╔════╝██╔════╝ ██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝
███████║█████╗  ██║  ███╗██║███████╗██║     ██║   ██║██████╔╝█████╗
██╔══██║██╔══╝  ██║   ██║██║╚════██║██║     ██║   ██║██╔══██╗██╔══╝
██║  ██║███████╗╚██████╔╝██║███████║╚██████╗╚██████╔╝██║  ██║███████╗
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
```

### **Self-Hosted AI Security Intelligence Platform**

*Predict risky code. Correlate findings across repos. Generate local AI fixes. Own your data.*

<br/>

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Queue-Redis_+_Celery-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Containers-Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

[![Ollama](https://img.shields.io/badge/LLM-Ollama_(Local)-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai)
[![Semgrep](https://img.shields.io/badge/Scanner-Semgrep-3B8BD4?style=for-the-badge&logo=semgrep&logoColor=white)](https://semgrep.dev)
[![Prometheus](https://img.shields.io/badge/Metrics-Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Monitoring-Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)](https://grafana.com)
[![scikit-learn](https://img.shields.io/badge/ML-scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

<br/>

> **AEGISCORE** is not a vulnerability scanner. It is a security intelligence platform.
> It learns from your repositories, forecasts where risk is accumulating,
> correlates findings across your entire organization, and drafts AI-generated
> fixes — all running on your own infrastructure. No data leaves your machine.

<br/>

</div>

---

## Table of Contents

- [The Problem](#the-problem)
- [What AEGISCORE Does Differently](#what-aegiscore-does-differently)
- [Architecture](#architecture)
  - [System Overview](#system-overview)
  - [Data Flow](#data-flow)
  - [AI Engine](#ai-engine)
  - [Scan Orchestration](#scan-orchestration)
- [Tech Stack](#tech-stack)
- [Core Features](#core-features)
  - [Vulnerability Risk Forecasting](#1-vulnerability-risk-forecasting)
  - [Cross-Repo Security Correlation](#2-cross-repo-security-correlation)
  - [Local AI Fix Generation](#3-local-ai-fix-generation)
  - [Multi-Team Platform](#4-multi-team-platform)
  - [Real-Time Scan Orchestration](#5-real-time-scan-orchestration)
  - [Developer Risk Patterns](#6-developer-risk-patterns)
  - [Sentinel CLI](#7-aegiscore-cli)
  - [Platform Self-Monitoring](#8-platform-self-monitoring)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [ML Model Reference](#ml-model-reference)
- [CLI Reference](#cli-reference)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [GitHub Actions Integration](#github-actions-integration)
- [Positioning vs Existing Tools](#positioning-vs-existing-tools)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## The Problem

Modern security tools are reactive. They tell you what broke after you pushed it. They scan one repo at a time. Their fixes are generic suggestions copy-pasted from documentation. And most critically — they send your code to a third-party server to analyze it.

The security workflow at most engineering teams looks like this:

```
Developer pushes code
        ↓
Scanner finds vulnerability (3-10 minutes later)
        ↓
Notification sent to security team
        ↓
Security team manually reviews
        ↓
Developer gets a ticket: "fix this"
        ↓
Developer fixes it (maybe, eventually)
```

This is a broken loop. It is slow, manual, reactive, and disconnected from how developers actually work. It also treats each repository as an isolated unit — ignoring the fact that vulnerabilities spread through shared dependencies, common patterns, and repeated mistakes across an organization's entire codebase.

---

## What AEGISCORE Does Differently

AEGISCORE shifts the security model from reactive detection to **predictive intelligence**.

| Capability | Traditional Scanners | GitHub Advanced Security | AEGISCORE |
|-----------|---------------------|------------------------|-----------|
| Finds known vulnerabilities | Yes | Yes | Yes |
| Multi-language support | Partial | Yes | Yes |
| Cross-repo correlation | No | No | **Yes** |
| Vulnerability risk forecasting | No | No | **Yes** |
| AI-generated fixes | No | Copilot only (cloud) | **Yes (local, private)** |
| Self-hosted / air-gapped | Partial | No | **Yes** |
| Multi-team organization management | Partial | Yes | **Yes** |
| Trains on your own repo history | No | No | **Yes** |
| Platform self-monitoring | No | No | **Yes** |
| CLI with predict + fix commands | No | No | **Yes** |
| Data leaves your infrastructure | Yes | Yes | **Never** |

The positioning is precise: AEGISCORE is a **self-hosted, org-wide security intelligence platform** that combines scanning, ML-based risk forecasting, cross-repo correlation, and local LLM-powered fix generation in a single deployable stack.

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ORGANIZATION BOUNDARY                               │
│                                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   repo-A     │    │   repo-B     │    │   repo-C     │    │   repo-N     │  │
│  │  (Team Alfa) │    │  (Team Alfa) │    │  (Team Beta) │    │  (Team Beta) │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │                   │          │
│         └───────────────────┴───────────────────┴───────────────────┘          │
│                                       │ git push → GitHub Actions webhook        │
│                                       ▼                                          │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                         AEGISCORE PLATFORM                                  │ │
│  │                                                                              │ │
│  │  ┌─────────────┐    ┌──────────────────────────────────────────────────┐   │ │
│  │  │  FastAPI    │    │              CELERY WORKER POOL                   │   │ │
│  │  │  REST API   │───▶│                                                   │   │ │
│  │  │  :8000      │    │  Worker-1: Semgrep scan    Worker-3: Bandit scan  │   │ │
│  │  └──────┬──────┘    │  Worker-2: Trivy scan      Worker-4: ML training  │   │ │
│  │         │           └──────────────────┬───────────────────────────────┘   │ │
│  │         │                              │                                    │ │
│  │  ┌──────▼──────┐    ┌─────────────┐   │   ┌──────────────────────────┐    │ │
│  │  │  PostgreSQL │    │    Redis    │◀──┘   │    AI ENGINE              │    │ │
│  │  │  :5432      │    │    :6379    │       │                            │    │ │
│  │  │             │    │  Task queue │       │  Risk Forecasting Model    │    │ │
│  │  │  orgs       │    │  Result     │       │  (scikit-learn Random      │    │ │
│  │  │  teams      │    │  cache      │       │   Forest, retrained        │    │ │
│  │  │  users      │    │  Rate limit │       │   every 10 scans)          │    │ │
│  │  │  repos      │    └─────────────┘       │                            │    │ │
│  │  │  scans      │                          │  Fix Generator             │    │ │
│  │  │  findings   │    ┌─────────────┐       │  (Ollama local LLM         │    │ │
│  │  │  risk_scores│    │   Ollama    │◀──────│   codellama:7b)            │    │ │
│  │  │  risk_history    │   :11434    │       └──────────────────────────┘    │ │
│  │  └─────────────┘    └─────────────┘                                        │ │
│  │                                                                              │ │
│  │  ┌─────────────┐    ┌─────────────┐                                        │ │
│  │  │  Prometheus │    │   Grafana   │                                        │ │
│  │  │  :9090      │───▶│   :3001     │                                        │ │
│  │  └─────────────┘    └─────────────┘                                        │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                       │                                          │
│                                       ▼                                          │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                         REACT PLATFORM UI  :3000                            │ │
│  │   Org Dashboard │ Team View │ Repo Detail │ Risk Map │ Fix Review │ CLI     │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

The complete journey from a `git push` to an AI-generated fix suggestion:

```
Step 1  Developer pushes to any connected repository
        ↓
Step 2  GitHub Actions webhook fires → POST /api/v1/scans/trigger
        Payload: { repo_id, commit_sha, branch, diff_patch }
        ↓
Step 3  FastAPI validates JWT, enqueues 3 parallel Celery tasks:
        Task A → Semgrep scan (OWASP Top 10 + custom rules)
        Task B → Bandit scan (Python-specific security checks)
        Task C → Trivy scan (dependency & container vulnerabilities)
        ↓
Step 4  Each worker completes independently, writes findings to PostgreSQL
        Redis tracks task status → dashboard polls for real-time updates
        ↓
Step 5  On all 3 tasks complete, Correlation Engine runs:
        Checks if any finding's file_path or rule_id matches findings
        in other repos across the org → creates cross_repo_links records
        ↓
Step 6  AI Engine triggers risk score recalculation for affected files:
        Pulls git log features for each changed file
        Feeds into trained Random Forest model
        Updates risk_scores table with new likelihood scores
        ↓
Step 7  For each CRITICAL or HIGH finding:
        Sends vulnerable code snippet + context to Ollama codellama:7b
        Receives suggested fix as unified diff
        Stores as fix_suggestions record linked to finding
        ↓
Step 8  If finding count crosses alert threshold:
        Slack webhook fires with org-level summary
        ↓
Step 9  React dashboard updates via polling:
        New findings appear in table
        Risk heatmap updates for affected files
        Cross-repo correlation badges appear
        Fix suggestions available for review
        ↓
Step 10 Every 10 scans: ML model retraining job queues automatically
        Pulls latest scan history from PostgreSQL
        Retrains Random Forest on new data
        Saves updated model artifact to disk
        Accuracy metrics published to Prometheus
```

### AI Engine

The AI Engine has two distinct components with different responsibilities:

```
┌───────────────────────────────────────────────────────────────────┐
│                    RISK FORECASTING MODEL                          │
│                                                                    │
│  Input features extracted from git history per file:              │
│    - commit_frequency_30d     (how often this file changes)       │
│    - author_count             (how many developers touched it)    │
│    - avg_diff_size            (average lines changed per commit)  │
│    - past_vuln_count          (historical vulnerability count)    │
│    - days_since_last_vuln     (recency of last finding)           │
│    - file_complexity_score    (cyclomatic complexity via radon)   │
│    - import_risk_score        (risk score of imported modules)    │
│    - test_coverage_ratio      (from coverage.xml if present)      │
│                                                                    │
│  Model: Random Forest Classifier (scikit-learn)                   │
│  Output: risk_score (0.0 to 1.0) per file                        │
│  Label: "vulnerability likelihood" (not certainty)                │
│  Retraining: automatic every 10 completed scans                   │
│  Minimum training data: 50 scan records                           │
│                                                                    │
│  NOTE: Score is a relative likelihood signal derived from your    │
│  organization's own historical data — not a universal classifier. │
└───────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│                    LOCAL AI FIX GENERATOR                          │
│                                                                    │
│  Model: codellama:7b via Ollama (runs 100% locally)               │
│  Trigger: any finding with severity CRITICAL or HIGH              │
│                                                                    │
│  Prompt structure sent to Ollama:                                 │
│    - Vulnerability type and CWE identifier                        │
│    - File path and programming language                           │
│    - 10 lines before + vulnerable lines + 10 lines after         │
│    - Semgrep rule message                                         │
│    - Instruction: return unified diff format only                 │
│                                                                    │
│  Output stored as:                                                │
│    - unified diff (ready to apply with `git apply`)              │
│    - plain English explanation of the fix                         │
│    - confidence indicator (high/medium/low based on model temp)  │
│                                                                    │
│  Data privacy: code never leaves your machine.                    │
│  Ollama runs entirely in a Docker container on your server.       │
└───────────────────────────────────────────────────────────────────┘
```

### Scan Orchestration

```
                        POST /api/v1/scans/trigger
                                   │
                    ┌──────────────▼──────────────┐
                    │      FastAPI validates       │
                    │  JWT + repo membership +     │
                    │  rate limit check (Redis)    │
                    └──────────────┬──────────────┘
                                   │
               ┌───────────────────┼───────────────────┐
               │                   │                   │
               ▼                   ▼                   ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │  Celery Task A  │  │  Celery Task B  │  │  Celery Task C  │
    │  semgrep_scan   │  │  bandit_scan    │  │  trivy_scan     │
    │                 │  │                 │  │                 │
    │ Runs in Worker1 │  │ Runs in Worker2 │  │ Runs in Worker3 │
    │ ~15-45 seconds  │  │ ~5-20 seconds   │  │ ~10-30 seconds  │
    └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │ all complete
                                  ▼
                    ┌─────────────────────────┐
                    │   Correlation Engine    │
                    │   (Task D, triggered    │
                    │    after A+B+C done)    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Risk Score Update     │
                    │   (Task E)              │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   AI Fix Generation     │
                    │   (Task F, per finding) │
                    └─────────────────────────┘
```

---

## Tech Stack

| Component | Technology | Version | Justification |
|-----------|-----------|---------|--------------|
| API Framework | FastAPI | 0.111+ | Async-native, automatic OpenAPI docs, 3x faster than Flask for concurrent scan jobs |
| Task Queue | Celery | 5.x | Distributes scan jobs across workers; handles retries, timeouts, chaining |
| Message Broker | Redis | 7.x | Celery broker + result backend + rate limiting + dashboard polling cache |
| Database | PostgreSQL | 16 | Multi-tenant relational data; JSONB for flexible finding metadata |
| ORM | SQLAlchemy 2 + Alembic | 2.x | Async ORM + database migrations |
| ML Engine | scikit-learn | 1.5+ | Random Forest for risk forecasting; lightweight, no GPU required |
| Code Complexity | Radon | Latest | Extracts cyclomatic complexity features for ML model |
| Local LLM | Ollama (codellama:7b) | Latest | Self-hosted LLM for fix generation; zero data egress |
| SAST Scanner | Semgrep | Latest | OWASP Top 10 + custom rules; JSON output |
| SAST Scanner | Bandit | Latest | Python-specific security checks |
| SCA Scanner | Trivy | Latest | Dependency and container vulnerability scanning |
| Auth | python-jose + bcrypt | Latest | JWT token auth + password hashing |
| Frontend | React 18 + Vite 5 | Latest | Platform UI |
| Charts | Recharts | 2.x | Risk heatmaps, trend charts |
| Monitoring | Prometheus | Latest | Metrics collection from FastAPI + Celery |
| Dashboards | Grafana | Latest | Platform health visualization |
| CLI | Python Click | 8.x | `aegiscore` command-line tool |
| Containers | Docker + Compose V2 | Latest | Full stack orchestration |

---

## Core Features

### 1. Vulnerability Risk Forecasting

AEGISCORE trains a Random Forest classifier on your organization's own scan history. After a minimum of 50 scan records, it begins producing a **vulnerability likelihood score** (0.0–1.0) for every file in every connected repository.

This is not a certainty score. It is a relative signal — "this file has characteristics that, in your organization's history, have correlated with security findings." It is most useful for:

- Prioritizing code review attention on high-risk files before a PR merges
- Identifying files that consistently attract vulnerabilities (structural code quality issues)
- Tracking whether refactoring efforts are reducing risk scores over time

The model retrains automatically every 10 completed scans using the latest data in your PostgreSQL database. Accuracy metrics (precision, recall, F1) are published to Prometheus after each training run and visible in Grafana.

**Risk score display in the platform:**

```
Repository: api-service                    Last scan: 4 minutes ago

File Risk Heatmap
─────────────────────────────────────────────────────────────
app/auth/views.py          ████████████████████  0.91  CRITICAL RISK
app/api/serializers.py     ███████████████       0.74  HIGH RISK
app/utils/crypto.py        ████████████          0.61  MEDIUM RISK
app/models/user.py         ████████              0.41  LOW RISK
app/config/settings.py     ████                  0.19  MINIMAL RISK
─────────────────────────────────────────────────────────────
Model trained on 847 historical scans · Last retrained: 2h ago
```

### 2. Cross-Repo Security Correlation

When a vulnerability is found in `repo-A`, AEGISCORE checks every other repository in the organization for the same finding signature — same rule ID, same import pattern, or same vulnerable function call.

If a match is found, both findings are linked in the `cross_repo_links` table and surface in the dashboard as correlated findings.

**Why this matters:** A shared utility library used across 6 repos may have a vulnerability. Without cross-repo correlation, a scanner flags it in `repo-A` and stops. AEGISCORE flags it in all 6 simultaneously, shows you the propagation graph, and generates one fix that applies to all of them.

```
Cross-repo correlation detected
───────────────────────────────────────────────────────────────────
Rule: python.lang.security.audit.hardcoded-password
Severity: CRITICAL

Found in 4 repositories:
  repo-A / app/config.py:22           (Team Alfa)   scan #1042
  repo-B / src/settings.py:8          (Team Alfa)   scan #1044
  repo-D / backend/config/base.py:31  (Team Beta)   scan #1039
  repo-F / app/core/config.py:15      (Team Gamma)  scan #1041

Suggested action: Apply AI-generated fix to shared config pattern
across all 4 repositories simultaneously.
───────────────────────────────────────────────────────────────────
```

### 3. Local AI Fix Generation

For every CRITICAL or HIGH severity finding, AEGISCORE sends the vulnerable code and its context to a locally-running Ollama instance (model: `codellama:7b`). The model returns a concrete fix as a unified diff.

**The key property: your code never leaves your infrastructure.** Ollama runs inside a Docker container on your own server. No API calls to OpenAI, Anthropic, or any external service. This makes AEGISCORE safe for organizations with strict data residency requirements.

Example fix suggestion output:

```
Finding:  python.lang.security.audit.use-defused-xml
File:     app/parsers/xml_handler.py  line 34
Severity: HIGH
CWE:      CWE-611 (Improper Restriction of XML External Entity Reference)

AI-Generated Fix (confidence: high)
─────────────────────────────────────────────────────────
--- a/app/parsers/xml_handler.py
+++ b/app/parsers/xml_handler.py
@@ -31,7 +31,8 @@
-import xml.etree.ElementTree as ET
+import defusedxml.ElementTree as ET

 def parse_config(xml_string: str):
-    tree = ET.fromstring(xml_string)
+    tree = ET.fromstring(xml_string, forbid_dtd=True)
     return tree

Explanation:
  The standard xml.etree.ElementTree is vulnerable to XML External
  Entity (XXE) attacks. Replacing it with defusedxml disables DTD
  processing and external entity resolution by default. The
  forbid_dtd=True parameter makes this explicit.

Apply with:  git apply aegiscore_fix_finding_4821.patch
─────────────────────────────────────────────────────────
```

### 4. Multi-Team Platform

AEGISCORE is built as a proper multi-tenant platform from the ground up.

**Organization hierarchy:**

```
Organization (BYTEAEGIS)
├── Team: Alfa
│   ├── Members: alice, bob, charlie
│   └── Repositories: repo-A, repo-B, repo-C
├── Team: Beta
│   ├── Members: diana, evan
│   └── Repositories: repo-D, repo-E
└── Team: Gamma
    ├── Members: frank
    └── Repositories: repo-F
```

**Role permissions:**

| Action | Developer | Security Lead | Admin |
|--------|-----------|--------------|-------|
| View own team's findings | Yes | Yes | Yes |
| View other teams' findings | No | Yes | Yes |
| View cross-repo correlations | No | Yes | Yes |
| Trigger manual scans | Yes | Yes | Yes |
| Configure scan rules | No | Yes | Yes |
| Manage team members | No | No | Yes |
| Connect/disconnect repositories | No | Yes | Yes |
| View platform metrics (Grafana) | No | Yes | Yes |
| Manage organization settings | No | No | Yes |
| View ML model performance | No | Yes | Yes |

### 5. Real-Time Scan Orchestration

Celery workers handle scan jobs asynchronously. Multiple repositories can be scanning simultaneously without any blocking.

The platform dashboard shows live scan status:

```
Active Scans                                              Refresh: 8s ago
─────────────────────────────────────────────────────────────────────────
repo-A    commit a3f9d12   semgrep ████████████░░░░ 72%   ~12s remaining
repo-B    commit b8e2c91   bandit  ████████████████ done  23 findings
repo-C    commit f1a4d88   trivy   ████░░░░░░░░░░░░ 24%   ~31s remaining
repo-D    commit 9c3b2f7   queued  ░░░░░░░░░░░░░░░░        waiting
─────────────────────────────────────────────────────────────────────────
Workers online: 4 / 4    Queue depth: 1    Avg scan time (24h): 34s
```

### 6. Developer Risk Patterns

AEGISCORE analyzes anonymized commit metadata to identify patterns that have historically preceded vulnerability discoveries in your organization. This is not blame tracking — it is pattern intelligence.

Identified patterns are surfaced in the Security Lead dashboard only:

```
Risk Pattern Intelligence  (anonymized, last 90 days)
───────────────────────────────────────────────────────────────────
Pattern                           Correlation    Occurrences
───────────────────────────────────────────────────────────────────
Config file changes               0.78           34 incidents
Large diffs (>400 lines)         0.71           21 incidents
Auth module modifications         0.69           18 incidents
Dependency version bumps          0.64           29 incidents
Late commits (10pm–4am local)    0.51           12 incidents
───────────────────────────────────────────────────────────────────
Note: Correlation ≠ causation. Use for code review prioritization.
```

### 7. AEGISCORE CLI

A full command-line interface for developers who prefer working in the terminal.

```bash
# Authenticate
aegiscore auth login --org byteaegis --token <your-token>

# Scan a local directory and push results to the platform
aegiscore scan ./my-repo --repo-id repo-A

# Show per-file risk scores for a repository
aegiscore predict ./my-repo --repo-id repo-A --top 10

# Fetch and display AI-generated fix for a specific finding
aegiscore fix --finding-id 4821

# Show all active scans across your organization
aegiscore status --org byteaegis

# Show cross-repo correlations for a specific rule
aegiscore correlate --rule python.lang.security.audit.hardcoded-password

# Export findings report as JSON or CSV
aegiscore report --repo-id repo-A --format csv --output report.csv

# Show platform health summary
aegiscore health
```

### 8. Platform Self-Monitoring

AEGISCORE monitors itself using Prometheus metrics exposed by FastAPI and Celery, visualized in a Grafana dashboard.

**Metrics tracked:**

| Metric | Description |
|--------|-------------|
| `aegiscore_scans_total` | Total scan jobs completed, by status |
| `aegiscore_scan_duration_seconds` | Histogram of scan durations by scanner type |
| `aegiscore_queue_depth` | Current number of jobs waiting in Celery queue |
| `aegiscore_findings_total` | Total findings stored, by severity and repo |
| `aegiscore_ml_accuracy` | F1 score of risk model after each retraining |
| `aegiscore_fix_generation_seconds` | Time taken by Ollama to generate each fix |
| `aegiscore_api_request_duration_seconds` | FastAPI endpoint latency histogram |
| `aegiscore_active_workers` | Number of live Celery workers |

---

## Project Structure

```
aegiscore/
│
├── .env.example
├── .gitignore
├── README.md
├── docker-compose.yml
│
├── backend/
│   ├── alembic.ini                      # Database migration configuration
│   ├── config.py                        # All settings from environment variables
│   ├── database.py                      # PostgreSQL async engine + session factory
│   ├── Dockerfile                       # Backend container definition
│   ├── main.py                          # FastAPI app entry point
│   ├── requirements.txt                 # Python dependencies
│   │
│   ├── auth/
│   │   ├── dependencies.py              # FastAPI auth dependency injection
│   │   ├── jwt.py                       # JWT creation + verification
│   │   ├── rbac.py                      # Role-based access control decorators
│   │   └── __init__.py
│   │
│   ├── migrations/
│   │   ├── env.py                       # Alembic migration environment
│   │   ├── script.py.mako               # Migration template
│   │   └── versions/                    # Auto-generated migration files
│   │
│   ├── models/
│   │   ├── finding.py                   # Finding, CrossRepoLink ORM models
│   │   ├── fix.py                       # FixSuggestion ORM model
│   │   ├── org.py                       # Organization, Team, TeamMembership models
│   │   ├── repo.py                      # Repository, RepoBranch models
│   │   ├── risk.py                      # RiskScore, RiskHistory models
│   │   ├── scan.py                      # Scan, ScanTask models
│   │   ├── user.py                      # User, Role models
│   │   └── __init__.py
│   │
│   ├── routers/
│   │   ├── auth.py                      # Authentication endpoints
│   │   ├── correlations.py              # Cross-repo correlation API
│   │   ├── findings.py                  # Vulnerability findings API
│   │   ├── fixes.py                     # AI fix suggestion API
│   │   ├── metrics.py                   # Prometheus metrics endpoint
│   │   ├── orgs.py                      # Organization and team management
│   │   ├── repos.py                     # Repository management API
│   │   ├── risk.py                      # Risk scoring and heatmap API
│   │   ├── scans.py                     # Scan triggering and status API
│   │   └── __init__.py
│   │
│   ├── schemas/
│   │   ├── auth.py                      # Auth Pydantic schemas
│   │   ├── finding.py                   # Finding Pydantic schemas
│   │   ├── fix.py                       # Fix Pydantic schemas
│   │   ├── org.py                       # Org and Team Pydantic schemas
│   │   ├── risk.py                      # Risk Pydantic schemas
│   │   ├── scan.py                      # Scan Pydantic schemas
│   │   └── __init__.py
│   │
│   ├── services/
│   │   ├── alerts.py                    # Slack webhook notification service
│   │   ├── correlation.py               # Cross-repo finding correlation engine
│   │   ├── __init__.py
│   │   │
│   │   ├── ai/
│   │   │   ├── feature_extractor.py     # Git log feature extraction per file
│   │   │   ├── fix_generator.py         # Ollama API client for fix generation
│   │   │   ├── risk_model.py            # Random Forest training + prediction
│   │   │   └── __init__.py
│   │   │
│   │   └── scanner/
│   │       ├── bandit.py                # Bandit runner + output parser
│   │       ├── semgrep.py               # Semgrep runner + JSON parser
│   │       ├── trivy.py                 # Trivy runner + output parser
│   │       └── __init__.py
│   │
│   └── workers/
│       ├── celery_app.py                # Celery app init with Redis broker
│       ├── __init__.py
│       └── tasks/
│           ├── ai_tasks.py              # Risk scoring + fix generation tasks
│           ├── maintenance_tasks.py     # ML retraining + cleanup tasks
│           ├── scan_tasks.py            # Celery tasks for each scanner
│           └── __init__.py
│
├── cli/
│   ├── aegiscore_cli.py                 # Main CLI implementation (Click + Rich)
│   └── pyproject.toml                   # CLI package configuration
│
├── frontend/
│   ├── Dockerfile                       # Frontend container definition
│   ├── index.html                       # Application entry document
│   ├── nginx.conf                       # Production Nginx configuration
│   ├── package.json                     # Node.js dependencies
│   ├── vite.config.js                   # Vite build configuration
│   └── src/
│       ├── App.jsx                      # Main application component
│       ├── index.css                    # Global styles
│       ├── main.jsx                     # React entry point
│       │
│       ├── api/
│       │   ├── auth.js                  # Authentication API client
│       │   ├── client.js                # Axios instance with interceptors
│       │   ├── correlations.js          # Correlations API client
│       │   ├── findings.js              # Findings API client
│       │   ├── fixes.js                 # Fixes API client
│       │   ├── risk.js                  # Risk API client
│       │   └── scans.js                 # Scans API client
│       │
│       ├── components/
│       │   ├── correlation/             # Correlation visualization components
│       │   ├── dashboard/               # Dashboard widgets and cards
│       │   ├── findings/                # Finding tables and details
│       │   ├── fixes/                   # AI fix review components
│       │   ├── layout/                  # Main AppShell, Sidebar, Header
│       │   ├── risk/                    # Risk heatmaps and trend charts
│       │   └── ui/                      # Base UI design system components
│       │
│       ├── contexts/
│       │   ├── AuthContext.jsx          # User authentication state
│       │   └── OrgContext.jsx           # Organization selection state
│       │
│       ├── hooks/
│       │   ├── useAuth.js               # Auth convenience hook
│       │   ├── useOrg.js                # Org convenience hook
│       │   └── usePolling.js            # Real-time data polling hook
│       │
│       └── pages/
│           ├── CorrelationsPage.jsx     # Cross-repo correlation view
│           ├── DashboardPage.jsx        # Main overview dashboard
│           ├── FindingsPage.jsx         # Vulnerability explorer
│           ├── FixesPage.jsx            # AI fix management
│           ├── LoginPage.jsx            # Authentication page
│           ├── RepoPage.jsx             # Repository detailed view
│           └── RiskPage.jsx             # Risk forecasting dashboard
│
└── infra/
    └── prometheus.yml                   # Metrics collection configuration
```

---

## Database Schema

```
┌────────────────────────────────────────────────────────────────────────────┐
│  organizations                                                               │
│  ─────────────────────────────────────────────────────────────────────────  │
│  id (PK)  │  name  │  slug  │  created_at  │  plan  │  scan_count          │
└───────────────────────────────┬────────────────────────────────────────────┘
                                │ 1───N
┌───────────────────────────────▼────────────────────────────────────────────┐
│  teams                                                                       │
│  ─────────────────────────────────────────────────────────────────────────  │
│  id (PK)  │  org_id (FK)  │  name  │  slug  │  created_at                  │
└───────────────────────────────┬────────────────────────────────────────────┘
                    ┌───────────┴────────────┐
                    │ 1───N                  │ 1───N
┌───────────────────▼──────────┐  ┌─────────▼──────────────────────────────┐
│  team_memberships            │  │  repositories                           │
│  ────────────────────────    │  │  ─────────────────────────────────────  │
│  id  │  team_id  │  user_id  │  │  id  │  team_id  │  name  │  github_url │
│  role (ENUM: dev/lead/admin) │  │  default_branch  │  connected_at        │
└──────────────────────────────┘  └──────────────────┬──────────────────────┘
                                                      │ 1───N
┌─────────────────────────────────────────────────────▼──────────────────────┐
│  scans                                                                       │
│  ─────────────────────────────────────────────────────────────────────────  │
│  id  │  repo_id  │  commit_sha  │  branch  │  triggered_at  │  status       │
│  total_findings  │  critical  │  high  │  medium  │  low  │  duration_ms    │
└──────────────────────────────────────────┬─────────────────────────────────┘
                                           │ 1───N
┌──────────────────────────────────────────▼─────────────────────────────────┐
│  findings                                                                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│  id  │  scan_id  │  scanner (semgrep/bandit/trivy)  │  severity             │
│  rule_id  │  file_path  │  line_number  │  message  │  cwe  │  metadata     │
└────────────────────────┬─────────────────────────────────────────────────--┘
              ┌──────────┴──────────┐
              │ N───M               │ 1───1
┌─────────────▼────────┐  ┌────────▼────────────────────────────────────────┐
│  cross_repo_links    │  │  fix_suggestions                                 │
│  ────────────────    │  │  ────────────────────────────────────────────    │
│  id                  │  │  id  │  finding_id  │  model_used               │
│  finding_id_a        │  │  unified_diff  │  explanation  │  confidence     │
│  finding_id_b        │  │  generated_at  │  applied (bool)                │
│  correlation_type    │  └────────────────────────────────────────────────┘
│  discovered_at       │
└──────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  risk_scores                                                                 │
│  ─────────────────────────────────────────────────────────────────────────  │
│  id  │  repo_id  │  file_path  │  score (0.0–1.0)  │  calculated_at        │
│  model_version  │  feature_snapshot (JSONB)                                │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  risk_history                                                                │
│  ─────────────────────────────────────────────────────────────────────────  │
│  id  │  repo_id  │  file_path  │  score  │  scan_id  │  recorded_at        │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## API Reference

Base URL: `http://localhost:8000/api/v1`
Authentication: `Authorization: Bearer <jwt_token>` on all endpoints except `/auth/login`

---

### Authentication

**`POST /auth/login`**

```json
Request:  { "email": "user@org.com", "password": "..." }
Response: { "access_token": "...", "refresh_token": "...", "expires_in": 3600 }
```

**`POST /auth/refresh`**

```json
Request:  { "refresh_token": "..." }
Response: { "access_token": "...", "expires_in": 3600 }
```

---

### Scans

**`POST /scans/trigger`** — Queue a new scan for a repository

```json
Request: {
  "repo_id": "uuid",
  "commit_sha": "a3f9d12e...",
  "branch": "main",
  "scanners": ["semgrep", "bandit", "trivy"]
}
Response 202: {
  "scan_id": "uuid",
  "status": "queued",
  "task_ids": { "semgrep": "...", "bandit": "...", "trivy": "..." }
}
```

**`GET /scans`** — List scans with optional filters

Query params: `repo_id`, `branch`, `status`, `limit` (default 30), `offset`

**`GET /scans/{scan_id}`** — Get scan detail with all findings

**`GET /scans/{scan_id}/status`** — Get live task progress (for dashboard polling)

---

### Findings

**`GET /findings`**

Query params: `repo_id`, `severity`, `scanner`, `rule_id`, `limit`, `offset`

```json
Response: {
  "findings": [
    {
      "id": "uuid",
      "scan_id": "uuid",
      "scanner": "semgrep",
      "severity": "CRITICAL",
      "rule_id": "python.lang.security.audit.hardcoded-password",
      "file_path": "app/config.py",
      "line_number": 22,
      "message": "Hardcoded password detected",
      "cwe": "CWE-798",
      "correlated_repos": ["repo-B", "repo-D"],
      "has_fix": true
    }
  ],
  "total": 47,
  "returned": 30
}
```

---

### Risk Scores

**`GET /risk/heatmap`** — Returns risk scores for all files in a repo

Query params: `repo_id`, `min_score` (default 0.0), `limit` (default 50)

**`GET /risk/history`** — Returns risk score trend for a specific file over time

Query params: `repo_id`, `file_path`, `days` (default 30)

---

### Fix Suggestions

**`GET /fixes`** — List all generated fix suggestions

Query params: `finding_id`, `applied`, `confidence`, `limit`

**`POST /fixes/{fix_id}/apply`** — Mark a fix as applied (updates `applied=true`)

---

### Correlations

**`GET /correlations`** — List all cross-repo finding correlations

Query params: `rule_id`, `severity`, `repo_id`, `limit`

---

## ML Model Reference

**Model type:** `sklearn.ensemble.RandomForestClassifier`

**Training data source:** `scans` + `findings` tables in PostgreSQL

**Feature vector per file (8 features):**

```python
{
  "commit_frequency_30d":   int,    # number of commits touching this file in 30 days
  "author_count":           int,    # distinct git authors who modified this file
  "avg_diff_size":          float,  # average lines changed per commit
  "past_vuln_count":        int,    # total findings ever on this file
  "days_since_last_vuln":   int,    # days since most recent finding (9999 if never)
  "file_complexity_score":  float,  # cyclomatic complexity from radon (0.0–100.0)
  "import_risk_score":      float,  # average risk score of imported modules (0.0–1.0)
  "test_coverage_ratio":    float,  # test coverage ratio (0.0–1.0, 0.5 if unknown)
}
```

**Label:** `1` if file had a finding in the subsequent scan, `0` otherwise

**Minimum training records:** 50 completed scans

**Retraining trigger:** automatic after every 10 new completed scans

**Model artifact storage:** `backend/models/risk_model.pkl` (volume-mounted in Docker)

**Metrics published to Prometheus after each retraining:**
- `aegiscore_ml_precision`
- `aegiscore_ml_recall`
- `aegiscore_ml_f1_score`
- `aegiscore_ml_training_samples`

---

## CLI Reference

Install the CLI:

```bash
cd cli
pip install -e .
```

Full command reference:

```bash
# Authentication
aegiscore auth login                        # Interactive login
aegiscore auth login --email x --token y   # Non-interactive (for scripts)
aegiscore auth logout                       # Clear stored credentials
aegiscore auth whoami                       # Show current user + org

# Scanning
aegiscore scan ./path/to/repo               # Scan local directory
aegiscore scan ./path --repo-id <id>        # Link to platform repo
aegiscore scan ./path --scanners semgrep    # Run specific scanner only
aegiscore scan ./path --wait                # Block until scan completes

# Risk Forecasting
aegiscore predict ./path/to/repo            # Show all file risk scores
aegiscore predict ./path --top 10           # Show top 10 riskiest files
aegiscore predict ./path --min-score 0.7    # Show files above threshold
aegiscore predict ./path --file app/auth.py # Score a specific file only

# Fix Generation
aegiscore fix --finding-id <uuid>           # Fetch AI fix for a finding
aegiscore fix --finding-id <uuid> --apply   # Fetch fix and apply as git patch
aegiscore fix --scan-id <uuid>              # Fetch all fixes for a scan

# Status
aegiscore status                            # All active scans in your org
aegiscore status --repo-id <id>             # Active scans for one repo
aegiscore status --watch                    # Live-updating status (refresh 5s)

# Correlations
aegiscore correlate --rule <rule_id>        # Find correlated findings by rule
aegiscore correlate --finding-id <uuid>     # Find findings correlated to one

# Reports
aegiscore report --repo-id <id>             # Print findings summary to stdout
aegiscore report --repo-id <id> --format csv --output report.csv
aegiscore report --repo-id <id> --format json --output report.json

# Platform Health
aegiscore health                            # API status, worker count, queue depth
```

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Docker | Latest | [docker.com](https://docker.com) |
| Docker Compose V2 | Latest | Bundled with Docker Desktop |
| Python | 3.11+ | [python.org](https://python.org) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org) |
| Git | Any | [git-scm.com](https://git-scm.com) |
| Ollama | Latest | [ollama.ai](https://ollama.ai) (optional if using Docker) |

Minimum server specs for self-hosting:
- CPU: 4 cores (8 recommended for parallel scan workers)
- RAM: 8 GB minimum (16 GB recommended — Ollama codellama:7b needs ~5 GB)
- Disk: 20 GB minimum (model weights + database)

---

## Installation & Setup

### 1. Clone and configure

```bash
git clone https://github.com/BYTEGUARDIAN14/aegiscore.git
cd aegiscore
cp .env.example .env
# Edit .env with your values
```

### 2. Pull the Ollama model (one-time, ~4 GB download)

```bash
docker compose run --rm ollama ollama pull codellama:7b
```

### 3. Start the full stack

```bash
docker compose up --build
```

This starts: PostgreSQL, Redis, FastAPI, 4 Celery workers, Ollama, React frontend, Prometheus, Grafana.

### 4. Run database migrations

```bash
docker compose exec backend alembic upgrade head
```

### 5. Create your first organization and admin user

```bash
docker compose exec backend python scripts/create_org.py \
  --org-name "BYTEAEGIS" \
  --admin-email "admin@byteaegis.in" \
  --admin-password "your-secure-password"
```

### 6. Install the CLI

```bash
cd cli && pip install -e .
aegiscore auth login --email admin@byteaegis.in
```

### 7. Access the platform

| Service | URL |
|---------|-----|
| React Dashboard | http://localhost:3000 |
| FastAPI Docs | http://localhost:8000/docs |
| Grafana | http://localhost:3001 (admin/admin) |
| Prometheus | http://localhost:9090 |

---

## Configuration

```bash
# .env.example — copy to .env

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aegiscore
POSTGRES_USER=aegiscore
POSTGRES_PASSWORD=              # Set a strong password

# Redis
REDIS_URL=redis://localhost:6379/0

# FastAPI
SECRET_KEY=                     # python -c "import secrets; print(secrets.token_hex(32))"
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_WORKER_CONCURRENCY=4

# Ollama (local LLM)
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=codellama:7b
OLLAMA_TIMEOUT=120              # seconds; larger repos need more time

# ML Model
ML_MODEL_PATH=/app/models/risk_model.pkl
ML_RETRAIN_EVERY_N_SCANS=10
ML_MIN_TRAINING_SAMPLES=50

# Alerts
SLACK_WEBHOOK_URL=              # Optional
SLACK_ALERT_SEVERITY=CRITICAL   # Minimum severity to trigger alert

# Scanners
SEMGREP_RULES=p/owasp-top-ten,p/python,p/javascript
TRIVY_SEVERITY=HIGH,CRITICAL

# Frontend
VITE_API_URL=http://localhost:8000/api/v1

# Prometheus
PROMETHEUS_ENABLED=true
```

---

## GitHub Actions Integration

Add this single file to any repository to connect it to AEGISCORE:

```yaml
# .github/workflows/aegiscore.yml
name: AEGISCORE Security Scan

on:
  push:
    branches: [ "main", "develop" ]
  pull_request:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  aegiscore-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0          # Full history needed for ML features

      - name: Trigger AEGISCORE scan
        env:
          AEGISCORE_URL: ${{ secrets.AEGISCORE_URL }}
          AEGISCORE_TOKEN: ${{ secrets.AEGISCORE_TOKEN }}
          AEGISCORE_REPO_ID: ${{ secrets.AEGISCORE_REPO_ID }}
        run: |
          curl -s -X POST "$AEGISCORE_URL/api/v1/scans/trigger" \
            -H "Authorization: Bearer $AEGISCORE_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{
              "repo_id": "'"$AEGISCORE_REPO_ID"'",
              "commit_sha": "'"${{ github.sha }}"'",
              "branch": "'"${{ github.ref_name }}"'",
              "scanners": ["semgrep", "bandit", "trivy"]
            }'
```

One workflow file. One org-wide AEGISCORE instance. All repos connected.

---

## Positioning vs Existing Tools

ChatGPT's review of this project made a correct and important point — the honest positioning is not "nothing like this exists anywhere." The honest positioning is more precise and more powerful:

**AEGISCORE is the self-hosted, privacy-first alternative to GitHub Advanced Security + Copilot Autofix, built for engineering teams that need org-wide security intelligence without sending their code to a third-party cloud.**

| Aspect | GitHub Advanced Security | SonarQube | AEGISCORE |
|--------|-------------------------|-----------|-----------|
| Self-hosted | No | Yes | **Yes** |
| Data stays on your infra | No | Yes | **Yes** |
| Cross-repo correlation | No | No | **Yes** |
| ML risk forecasting on your history | No | No | **Yes** |
| AI fix generation | Copilot (cloud) | No | **Yes (local)** |
| Platform self-monitoring | No | Partial | **Yes** |
| CLI with predict + fix | No | No | **Yes** |
| Free and open source | No | Community only | **Yes** |
| Trains on your own codebase | No | No | **Yes** |

The combination is the differentiator. Not any single module.

---

## Roadmap

- [ ] **SARIF export** — Export findings in SARIF format for GitHub native code scanning UI integration
- [ ] **PR blocking** — Automatically block pull request merges when CRITICAL findings are detected
- [ ] **Webhook system** — Allow orgs to configure custom outbound webhooks on any event
- [ ] **Custom Semgrep rules editor** — Write and test custom detection rules from the platform UI
- [ ] **SBOM generation** — Generate Software Bill of Materials for each repository on scan
- [ ] **SSO / SAML** — Enterprise authentication integration
- [ ] **Kubernetes Helm chart** — Deploy to a K8s cluster with autoscaling Celery workers
- [ ] **VS Code extension** — Show risk scores and findings inline in the editor
- [ ] **Diff-only scanning** — Scan only changed lines in a PR (faster CI feedback)
- [ ] **Model marketplace** — Swap the local LLM model (codellama → mistral → llama3) from the UI
- [ ] **PDF / HTML report export** — Generate formatted security reports for stakeholders

---

## Contributing

1. Fork this repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Follow the commit convention below
4. Push and open a pull request against `main`

**Commit conventions:**

| Prefix | Use for |
|--------|---------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `ml:` | Changes to the risk model or AI engine |
| `docs:` | Documentation only |
| `refactor:` | Code restructuring, no behavior change |
| `chore:` | Dependency bumps, config, CI changes |

Please open an issue before starting work on large features.

---

## License

MIT License — see [LICENSE](LICENSE) for full text.

You are free to self-host, modify, and use AEGISCORE commercially. The only requirement is preserving the original copyright notice.

---

<div align="center">

<pre style="font-size:0.45em; line-height:1.2; letter-spacing:0;">
 █████╗ ███████╗ ██████╗ ██╗███████╗ ██████╗ ██████╗ ██████╗ ███████╗
██╔══██╗██╔════╝██╔════╝ ██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝
███████║█████╗  ██║  ███╗██║███████╗██║     ██║   ██║██████╔╝█████╗
██╔══██║██╔══╝  ██║   ██║██║╚════██║██║     ██║   ██║██╔══██╗██╔══╝
██║  ██║███████╗╚██████╔╝██║███████║╚██████╗╚██████╔╝██║  ██║███████╗
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
</pre>

**Mohamed Adhnaan J M** · BYTEAEGIS · [byteaegis.in](https://byteaegis.in) · [GitHub](https://github.com/BYTEGUARDIAN14)

`6176AC23UCS097`

*Security intelligence. Self-hosted. Yours.*

</div>