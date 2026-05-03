from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

from app.services.pipeline import run_pipeline
from app.services.memory_store import get_top_errors
from app.agents.github_agent import GitHubAgent
from app.services.issue_classifier import group_issues_llm

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LogRequest(BaseModel):
    log: str


@app.post("/analyze")
async def analyze(request: LogRequest):
    return run_pipeline(request.log)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    return run_pipeline(content.decode("utf-8"))


@app.get("/top-errors")
def top_errors():
    return {"top_errors": get_top_errors()}


@app.get("/issues")
def get_grouped_issues():
    github = GitHubAgent()
    issues = github.get_open_issues()
    grouped = group_issues_llm(issues)
    return {"groups": grouped}


@app.post("/close-issue/{issue_number}")
def close_issue(issue_number: int):
    github = GitHubAgent()
    success = github.close_issue(int(issue_number))
    return {
        "success": success,
        "issue_number": issue_number
    }