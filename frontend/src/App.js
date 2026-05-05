import { Activity, Bug, CheckCircle2, Play, RefreshCw, Send, XCircle } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import "./App.css";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

function App() {
  const [log, setLog] = useState("ERROR api.orders: HTTP 500 Internal Server Error while POST /orders");
  const [analysis, setAnalysis] = useState(null);
  const [topErrors, setTopErrors] = useState([]);
  const [issues, setIssues] = useState({});
  const [traces, setTraces] = useState([]);
  const [evalReport, setEvalReport] = useState(null);
  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");

  const issueCount = useMemo(
    () => Object.values(issues).reduce((sum, group) => sum + group.length, 0),
    [issues]
  );

  const request = useCallback(async (path, options) => {
    const response = await fetch(`${API_BASE}${path}`, options);
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }
    return response.json();
  }, []);

  const refresh = useCallback(async () => {
    setError("");
    try {
      const [top, issueGroups, traceData] = await Promise.all([
        request("/top-errors"),
        request("/issues"),
        request("/traces?limit=40"),
      ]);
      setTopErrors(top.top_errors || []);
      setIssues(issueGroups.groups || {});
      setTraces((traceData.traces || []).reverse());
    } catch (err) {
      setError(`Refresh failed: ${err.message}`);
    }
  }, [request]);

  const refreshIssues = useCallback(async () => {
    setLoading("issues");
    setError("");
    try {
      const issueGroups = await request("/issues");
      setIssues(issueGroups.groups || {});
    } catch (err) {
      setError(`Issue refresh failed: ${err.message}`);
    } finally {
      setLoading("");
    }
  }, [request]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const analyze = async () => {
    setLoading("analyze");
    setError("");
    try {
      const result = await request("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ log }),
      });
      setAnalysis(result);
      await refresh();
    } catch (err) {
      setError(`Analyze failed: ${err.message}`);
    } finally {
      setLoading("");
    }
  };

  const runEval = async () => {
    setLoading("eval");
    setError("");
    setEvalReport(null);
    try {
      const report = await request("/eval/run", { method: "POST" });
      setEvalReport(report);
      await refresh();
    } catch (err) {
      setError(`Eval failed: ${err.message}`);
    } finally {
      setLoading("");
    }
  };

  const closeIssue = async (number) => {
    setLoading(`close-${number}`);
    setError("");
    try {
      await request(`/close-issue/${number}`, { method: "POST" });
      await refreshIssues();
    } catch (err) {
      setError(`Close failed: ${err.message}`);
    } finally {
      setLoading("");
    }
  };

  const report = analysis?.final_report;

  return (
    <main className="app-shell">
      <section className="topbar">
        <div>
          <p className="eyebrow">Agentic issue triage</p>
          <h1>Sentinel Dashboard</h1>
        </div>
        <div className="actions">
          <button className="icon-button" onClick={refresh} title="Refresh dashboard">
            <RefreshCw size={18} />
          </button>
          <button onClick={runEval} disabled={loading === "eval"}>
            <Play size={18} />
            {loading === "eval" ? "Running Eval..." : "Run Eval"}
          </button>
        </div>
      </section>

      {error && <div className="error-banner">{error}</div>}
      {loading === "eval" && (
        <div className="status-banner">
          Running 20 synthetic logs through the agent pipeline. This can take up to a minute if the LLM has to timeout and use fallback.
        </div>
      )}

      <section className="metrics-grid">
        <Metric icon={<Bug />} label="Open issues" value={issueCount} />
        <Metric icon={<Activity />} label="Trace spans" value={traces.length} />
        <Metric
          icon={<CheckCircle2 />}
          label="Eval precision"
          value={evalReport ? `${Math.round(evalReport.metrics.exact_case_precision * 100)}%` : "--"}
        />
      </section>

      <section className="workbench">
        <div className="panel analyzer">
          <div className="panel-head">
            <h2>Analyze Log</h2>
            <button onClick={analyze} disabled={loading === "analyze"}>
              <Send size={18} />
              Analyze
            </button>
          </div>
          <textarea value={log} onChange={(event) => setLog(event.target.value)} />
        </div>

        <div className="panel result">
          <h2>Latest Report</h2>
          {report ? (
            <div className="report-stack">
              <h3>{report.title}</h3>
              <p>{report.root_cause}</p>
              <div className="chips">
                <span>{report.classification}</span>
                <span>{report.error_type}</span>
                <span>{report.analysis_source}</span>
              </div>
              <ol>
                {(report.fix_steps || []).map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ol>
              {report.regression_test?.should_add_test && (
                <pre className="test-snippet">{report.regression_test.test_code}</pre>
              )}
            </div>
          ) : (
            <p className="empty">Run an analysis to see the generated report.</p>
          )}
        </div>
      </section>

      <section className="data-grid">
        <div className="panel">
          <h2>Agent Traces</h2>
          <div className="trace-list">
            {traces.map((trace, index) => (
              <div className="trace-row" key={`${trace.timestamp}-${index}`}>
                <span className={trace.success ? "dot success" : "dot failed"} />
                <strong>{trace.agent}</strong>
                <span>{trace.latency_ms} ms</span>
                <span>{trace.input_tokens} tokens</span>
                <span>retry {trace.retry_count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <h2>Eval Report</h2>
          {evalReport ? (
            <div className="eval-summary">
              <div className="compact-row">
                <strong>Total samples</strong>
                <span>{evalReport.total_samples}</span>
              </div>
              <div className="compact-row">
                <strong>Title precision</strong>
                <span>{Math.round(evalReport.metrics.title_precision * 100)}%</span>
              </div>
              <div className="compact-row">
                <strong>Classification precision</strong>
                <span>{Math.round(evalReport.metrics.classification_precision * 100)}%</span>
              </div>
              <div className="compact-row">
                <strong>Exact case precision</strong>
                <span>{Math.round(evalReport.metrics.exact_case_precision * 100)}%</span>
              </div>
            </div>
          ) : (
            <p className="empty">Click Run Eval to score the synthetic log suite.</p>
          )}
        </div>
      </section>

      <section className="data-grid">
        <div className="panel">
          <h2>Recurring Errors</h2>
          <div className="compact-list">
            {topErrors.map(([key, item]) => (
              <div className="compact-row" key={key}>
                <strong>{item.error_type}</strong>
                <span>{item.count} seen</span>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <h2>Recent Eval Cases</h2>
          <div className="compact-list">
            {(evalReport?.cases || []).slice(0, 8).map((item) => (
              <div className="compact-row" key={item.id}>
                <strong>{item.id}</strong>
                <span>{Math.round(item.evaluation.score * 100)}%</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-head">
          <h2>GitHub Issues</h2>
          <button
            className="secondary-button"
            onClick={refreshIssues}
            disabled={loading === "issues" || loading.startsWith("close-")}
          >
            <RefreshCw size={18} />
            Refresh Issues
          </button>
        </div>
        <div className="issue-grid">
          {Object.entries(issues).length === 0 && (
            <p className="empty">No open GitHub issues found.</p>
          )}
          {Object.entries(issues).map(([group, groupIssues]) => (
            <div className="issue-group" key={group}>
              <h3>{group}</h3>
              {groupIssues.map((issue) => (
                <div className="issue-row" key={issue.number}>
                  <a href={issue.url} target="_blank" rel="noreferrer">
                    #{issue.number} {issue.title}
                  </a>
                  <button
                    className="icon-button danger"
                    onClick={() => closeIssue(issue.number)}
                    disabled={loading === `close-${issue.number}`}
                    title="Close issue"
                  >
                    <XCircle size={18} />
                  </button>
                </div>
              ))}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

function Metric({ icon, label, value }) {
  return (
    <div className="metric">
      <div className="metric-icon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default App;
