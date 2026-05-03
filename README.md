# 🤖 AI-Powered Agentic Issue Triage System

An end-to-end AI-driven system that analyzes application logs, identifies root causes, groups recurring failures, and integrates with GitHub Issues for automated tracking and resolution.

---

## 📋 Overview

Modern systems generate large volumes of logs, but debugging remains largely manual and inefficient. This project automates the entire triage workflow:

- Parses raw logs into structured data
- Uses LLMs to identify root causes and fixes
- Groups recurring errors to prevent duplication
- Automatically creates or reuses GitHub issues
- Provides a UI for monitoring and issue management

---

## 🏗️ Architecture

```
Logs → LogParserAgent → RootCauseAgent (LLM) → BugReportAgent → Memory Store → GitHub Integration
```

---

## ⚙️ Core Components

### `LogParserAgent`
Extracts structured signals from raw logs:
- Error messages
- Stack traces
- Contextual information

### `RootCauseAgent` *(LLM-based)*
Uses the Anthropic API to:
- Classify error type
- Identify root cause
- Suggest remediation steps

### `BugReportAgent`
Generates structured bug reports:
- Title
- Description
- Fix steps

### `TaggingAgent`
Automatically assigns tags such as: `backend`, `database`, `infrastructure`, `API`

### Memory Store *(Error Grouping)*
Tracks recurring failures and prevents duplicate issues:

```json
{
  "error_type": "HTTP 500",
  "root_cause": "Database connection timeout",
  "count": 47,
  "issue_url": "https://github.com/yourusername/repo/issues/42"
}
```

### GitHub Integration
- Creates issues for new error groups
- Reuses existing issues for repeated failures
- Enables closing issues via API/UI

---

## 🧠 LLM Usage

The system leverages LLMs for:
- Semantic error classification
- Root cause reasoning
- Fix recommendation generation
- Issue grouping

**Example LLM output:**

```python
analysis = {
    "error_type": "Internal Server Error",
    "root_cause": "Database connection timeout",
    "fix_steps": [
        "Increase DB pool size",
        "Add retry logic"
    ]
}
```

### Issue Classification Categories
Classification is **LLM-driven** (not rule-based), grouping issues into:
- Server Errors
- Database Failures
- Upstream Service Issues
- Transient Failures

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze` | Analyze submitted logs |
| `POST` | `/upload` | Upload log files |
| `GET` | `/top-errors` | Retrieve top recurring errors |
| `GET` | `/issues` | Get grouped GitHub issues |
| `POST` | `/close-issue/{issue_number}` | Close a specific issue |

---

## 🎯 Features

- ✅ LLM-based debugging
- ✅ Automatic root cause detection
- ✅ Smart grouping of recurring errors
- ✅ GitHub issue automation
- ✅ UI dashboard for monitoring
- ✅ Tagging + classification
- ✅ Persistent memory store

---

## 🖥️ Frontend Dashboard

- Analyze logs
- View grouped issues
- Close issues from UI
- Track recurring failures

**Example input/output:**

```
Input:  HTTP 500 Internal Server Error

Output:
  Error Type:  Internal Server Error
  Root Cause:  Backend service failure
  Fix Steps:
    - Check application logs
    - Restart the service
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Python, Uvicorn |
| AI / LLM | Anthropic API |
| Frontend | React.js |
| Integration | GitHub API |

---

## 🚀 Setup

**Clone and install:**

```bash
git clone https://github.com/yourusername/Agent_Triage_System.git
cd Backend
pip install -r requirements.txt
```

**Environment variables — create a `.env` file:**

```env
ANTHROPIC_API_KEY=your_anthropic_key
GITHUB_TOKEN=your_github_token
GITHUB_REPO=username/repo
```

---

## 💡 Why This Project?

Demonstrates real-world engineering skills:

- **Agentic AI systems** — multi-agent orchestration
- **LLM integration** — production-grade Anthropic API usage
- **System design** — modular, scalable architecture
- **Automation** — end-to-end engineering workflow

---

## 📦 Use Cases

- DevOps automation
- Incident management
- Log intelligence systems
- AI-assisted debugging tools

---

## 📈 Future Improvements

- [ ] Vector DB for semantic deduplication
- [ ] Real-time log ingestion
- [ ] Slack / Email alerts
- [ ] Advanced analytics dashboard