# AI-Powered Agentic Issue Triage System

An end-to-end AI-driven system that analyzes application logs, identifies root causes, groups recurring failures, and integrates with GitHub Issues for automated tracking and resolution.

---

## Overview

Modern systems generate large volumes of logs, but debugging remains largely manual and inefficient. This project automates the entire triage workflow:

- Parses raw logs into structured data  
- Uses LLMs to identify root causes and fixes  
- Groups recurring errors to prevent duplication  
- Automatically creates or reuses GitHub issues  
- Provides a UI for monitoring and issue management  

---

## Architecture

Logs → LogParserAgent → RootCauseAgent (LLM) → BugReportAgent → Memory Store → GitHub Integration

---

## Core Components

### LogParserAgent
Extracts structured signals from raw logs:
- Error messages  
- Stack traces  
- Contextual information  

---

### RootCauseAgent (LLM-based)
Uses an LLM (Anthropic API) to:
- Classify error type  
- Identify root cause  
- Suggest remediation steps  

---

### BugReportAgent
Generates structured bug reports:
- Title  
- Description  
- Fix steps  

---

### TaggingAgent
Automatically assigns tags such as:
- backend  
- database  
- infrastructure  
- API  

---

### Memory Store (Error Grouping)
Tracks recurring failures and prevents duplicate issues:

```json
{
  "error_type": "HTTP 500",
  "root_cause": "Database connection timeout",
  "count": 47,
  "issue_url": "..."
}



GitHub Integration
Creates issues for new error groups
Reuses existing issues for repeated failures
Enables closing issues via API/UI
LLM-Based Issue Classification

Groups issues semantically into categories such as:

Server Errors
Database Failures
Upstream Service Issues
Transient Failures

This is not rule-based; classification is driven by the LLM.

LLM Usage

The system leverages LLMs for:

Semantic error classification
Root cause reasoning
Fix recommendation generation
Issue grouping

Example output:

analysis = {
    "error_type": "Internal Server Error",
    "root_cause": "Database connection timeout",
    "fix_steps": ["Increase DB pool size", "Add retry logic"]
}



🌐 API Endpoints


Analyze Logs-->POST /analyze

Upload Logs-->POST /upload

Get Top Errors-->GET /top-errors

Get Grouped GitHub Issues-->GET /issues

Close Issue-->POST /close-issue/{issue_number}


🎯 Features

✔ LLM-based debugging
✔ Automatic root cause detection
✔ Smart grouping of recurring errors
✔ GitHub issue automation
✔ UI dashboard for monitoring
✔ Tagging + classification
✔ Persistent memory store



🖥️ Frontend Dashboard
Analyze logs
View grouped issues
Close issues from UI
Track recurring failures


Example Input-->HTTP 500 Internal Server Error

Error Type: Internal Server Error
Root Cause: Backend service failure
Fix Steps:
- Check logs
- Restart service


Tech Stack

Backend
--FastAPI
--Python
--Uvicorn

AI / LLM
--Anthropic API

Frontend
--React.js

Integration
---GitHub API

Setup-->>

git clone https://github.com/yourusername/Agent_Triage_System.git
cd Backend
pip install -r requirements.txt

Environment Variables

Create .env:

ANTHROPIC_API_KEY=your_key
GITHUB_TOKEN=your_token
GITHUB_REPO=username/repo



Why This is Valuable

This project demonstrates:

Agentic AI systems
LLM integration in production workflows
System design thinking
Automation of real-world engineering tasks


🎯 Use Cases:--
DevOps automation
Incident management
Log intelligence systems
AI-assisted debugging tools


📈 Future Improvements:--
Vector DB for semantic dedup
Real-time log ingestion
Slack/Email alerts
Advanced analytics dashboard

