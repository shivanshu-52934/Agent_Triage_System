# Sentinel: Agentic Issue Triage System

![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/frontend-React-1463A5)
![LLM](https://img.shields.io/badge/LLM-Anthropic-5B5FC7)
![Eval](https://img.shields.io/badge/eval-20%20synthetic%20cases-13795B)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-24292F)

Sentinel is an AI-powered debugging and issue triage platform. It accepts raw application logs, identifies likely root causes, generates actionable bug reports, groups recurring failures, and can create or reuse GitHub Issues automatically.

The project is designed like a production agent system rather than a simple prompt wrapper: it includes structured tracing, LLM output validation, retry and fallback paths, eval scoring, recurrence memory, a React operations dashboard, and GitHub Actions integration for failed CI runs.

## Highlights

- Multi-agent pipeline: `LogParser -> RootCause -> BugReport -> Tagging -> TestGeneration`.
- Anthropic-powered root-cause analysis with structured JSON output.
- LLM response validation, simplified retry, and rule-based fallback recovery.
- Smart recurrence tracking through a persistent local memory store.
- GitHub Issue automation with safe deduplication through stored error groups.
- Structured agent tracing with latency, token estimate, retry count, and success status.
- Evaluation harness with 20 labeled synthetic logs and precision metrics.
- React dashboard for log analysis, trace visibility, eval results, recurring errors, and issue management.
- GitHub Actions workflow that comments triage summaries on PRs when CI fails.
- Honest limitations documented for production readiness and future hardening.

## Architecture

```text
Raw Logs
  |
  v
LogParserAgent
  |
  v
RootCauseAgent
  |-- validates LLM JSON
  |-- retries malformed output once
  |-- falls back to rule-based classification
  v
BugReportAgent
  |
  v
TaggingAgent
  |
  v
TestGenerationAgent
  |
  +--> Memory Store
  +--> GitHub Issues
  +--> Trace Store
  +--> Eval Harness
  +--> React Dashboard
```

## Agent Pipeline

| Stage | Responsibility |
| --- | --- |
| `LogParserAgent` | Cleans and normalizes raw log text. |
| `RootCauseAgent` | Uses Anthropic to classify the failure, infer root cause, and suggest fixes. |
| `BugReportAgent` | Converts analysis into a structured title, description, priority, and confidence score. |
| `TaggingAgent` | Assigns operational tags such as backend, database, API, infrastructure, or performance. |
| `TestGenerationAgent` | Emits a pytest-style regression test draft for actionable failures. |
| `GitHubAgent` | Creates, lists, and closes GitHub Issues when repository credentials are configured. |

## Reliability Features

### LLM Failure Recovery

`RootCauseAgent` expects a strict schema:

```json
{
  "classification": "Critical Bug | Warning | Info",
  "error_type": "short label",
  "root_cause": "clear explanation",
  "fix_steps": ["step1", "step2", "step3"]
}
```

If the LLM returns malformed JSON or misses required fields, Sentinel retries once with a simpler prompt. If the retry still fails, it falls back to a deterministic rule-based classifier so the pipeline still returns a useful report.

### Structured Tracing

Every agent call is wrapped in a trace span. Spans are written as JSON lines to `agent_traces.jsonl` and exposed through `/traces`.

Example span:

```json
{
  "timestamp": "2026-05-05T18:21:20.745841",
  "agent": "RootCauseAgent",
  "input_tokens": 42,
  "latency_ms": 812.4,
  "retry_count": 1,
  "success": true
}
```

This makes it easy to see which agent ran, where time was spent, whether recovery paths were used, and where failures occurred.

### Evaluation Harness

The eval suite lives in `Backend/eval/`.

It runs 20 labeled synthetic logs through the same pipeline and writes:

```text
Backend/eval/eval_report.json
```

Metrics:

| Metric | Meaning |
| --- | --- |
| `title_precision` | Whether the generated title/error type matches the expected failure category. |
| `classification_precision` | Whether severity classification matches the expected label. |
| `exact_case_precision` | Whether the full eval case passed. |

Eval is not meant to run after every user analysis. It is a regression check for the AI pipeline, similar to a test suite.

## Dashboard

The React dashboard supports:

- Analyze a raw log.
- View generated root cause, fix steps, tags, and regression test draft.
- Run eval and inspect scoring metrics.
- View structured agent trace spans.
- View recurring error groups.
- View current open GitHub Issues.
- Close GitHub Issues from the UI.
- Refresh open issues after changes.

## Quickstart

### 1. Clone And Enter The Project

```powershell
cd C:\Users\shiva\Desktop\ats-copy
```

### 2. Backend Setup

```powershell
cd Backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Environment Variables

Create or edit `Backend/.env`:

```env
ANTHROPIC_API_KEY=your_anthropic_key
ANTHROPIC_MODEL=claude-haiku-4-5-20251001
GITHUB_TOKEN=
GITHUB_REPO=
TRACE_FILE=agent_traces.jsonl
```

For safe local testing, leave `GITHUB_TOKEN` and `GITHUB_REPO` empty. Sentinel will skip real GitHub issue creation.

### 4. Run Backend

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend URL:

```text
http://127.0.0.1:8000
```

### 5. Frontend Setup

Open a second terminal:

```powershell
cd C:\Users\shiva\Desktop\ats-copy\frontend
npm install
npm start
```

Dashboard URL:

```text
http://localhost:3000
```

## Manual Test

Use a safe warning-level log first:

```text
TimeoutError: request to payment provider timed out after 30000ms
```

Paste it into the dashboard and click `Analyze`.

Expected behavior:

- A root-cause report appears.
- Fix steps are generated.
- Tags are attached.
- A regression test draft appears.
- New trace spans appear in the dashboard.
- No GitHub Issue is created if GitHub env vars are empty.

## API Reference

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/analyze` | Analyze raw log text. |
| `POST` | `/upload` | Upload and analyze a log file. |
| `GET` | `/top-errors` | Return most frequent stored error groups. |
| `GET` | `/issues` | Return open GitHub Issues grouped by category. |
| `POST` | `/close-issue/{issue_number}` | Close a GitHub Issue. |
| `GET` | `/traces?limit=100` | Return recent agent trace spans. |
| `POST` | `/eval/run` | Run the synthetic eval suite. |

Example API call:

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/analyze `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"log":"TimeoutError: request timed out after 30000ms"}'
```

## Run Evaluation

From `Backend` with the virtual environment activated:

```powershell
python -m eval.run_eval
```

The report is written to:

```text
Backend/eval/eval_report.json
```

You can also run it from the dashboard with `Run Eval`.

## CI/CD Integration

The workflow file is located at:

```text
.github/workflows/sentinel.yml
```

It listens for failed `Tests` or `CI` workflow runs, downloads the failed logs, sends them to Sentinel, and comments the triage result on the related pull request.

Required GitHub secret:

```text
SENTINEL_API_URL=https://your-deployed-backend.example.com
```

## Project Structure

```text
.
|-- Backend
|   |-- app
|   |   |-- agents
|   |   |-- services
|   |   `-- main.py
|   |-- eval
|   |   |-- synthetic_logs.json
|   |   |-- run_eval.py
|   |   `-- eval_report.json
|   `-- requirements.txt
|-- frontend
|   |-- public
|   |-- src
|   `-- package.json
|-- .github
|   `-- workflows
|       `-- sentinel.yml
`-- README.md
```

## Production Notes

Sentinel is intentionally built with clear extension points:

- Replace local JSON memory with Postgres, Redis, or a vector store for production concurrency.
- Add auth before exposing GitHub issue controls publicly.
- Persist trace spans to OpenTelemetry, LangSmith, Honeycomb, or another observability backend.
- Expand eval data with real incident logs and project-specific expected answers.
- Turn generated regression test drafts into real PRs once repository test fixtures are known.

## Known Limitations

- LLM output can be overly specific, vague, or malformed. Sentinel validates the response, retries once, and falls back to rules.
- Rule-based fallback handles common patterns but cannot understand deep product context.
- Generated regression tests are templates and must be adapted to real fixtures before committing.
- GitHub issue creation requires a valid `GITHUB_TOKEN` and `GITHUB_REPO`.
- The local JSON memory store is not ideal for concurrent production writes.
- The eval suite is synthetic. It is useful for regression checks, not a guarantee of real-world accuracy.
- CI comments only work when the failed workflow is connected to a pull request.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Python, FastAPI, Uvicorn |
| LLM | Anthropic API |
| Frontend | React |
| Automation | GitHub API, GitHub Actions |
| Observability | JSONL trace spans |
| Evaluation | Synthetic log scoring harness |

## Positioning

Sentinel demonstrates practical agent engineering: orchestration, tool integration, LLM schema validation, fallback design, observability, evaluation, CI automation, and a working dashboard. It is built to show how AI can move beyond chat and become part of a real engineering workflow.
