import React, { useState } from "react";

function App() {
  const [log, setLog] = useState("");
  const [file, setFile] = useState(null);
  const [issues, setIssues] = useState({});
  const [selected, setSelected] = useState({});
  const [loading, setLoading] = useState(false);

  const API = "http://localhost:8000";

  // 🔥 ANALYZE LOGS
  const handleAnalyze = async () => {
    setLoading(true);

    try {
      let res;

      if (file) {
        const formData = new FormData();
        formData.append("file", file);

        res = await fetch(`${API}/upload`, {
          method: "POST",
          body: formData,
        });
      } else {
        res = await fetch(`${API}/analyze`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ log }),
        });
      }

      await res.json();
      alert("Analysis complete. Now load issues.");

    } catch (err) {
      console.error(err);
      alert("Error analyzing log");
    }

    setLoading(false);
  };

  // 🔥 LOAD ISSUES (MANUAL)
  const fetchIssues = async () => {
    try {
      const res = await fetch(`${API}/issues`);
      const data = await res.json();
      setIssues(data.groups || {});
    } catch (err) {
      console.error("Fetch failed", err);
    }
  };

  const toggleSelect = (id) => {
    setSelected(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const hasSelection = () => {
    return Object.values(selected).some(v => v);
  };

  const closeSelected = async () => {
    const ids = Object.keys(selected).filter(k => selected[k]);

    for (let id of ids) {
      await fetch(`${API}/close-issue/${id}`, {
        method: "POST"
      });
    }

    setSelected({});
    fetchIssues();
  };

  return (
    <div style={{ padding: "30px", fontFamily: "Arial", background: "#f5f7fa" }}>

      <h1>🚀 AI Issue Dashboard</h1>

      {/* ANALYZER */}
      <div style={{
        background: "#fff",
        padding: "20px",
        borderRadius: "10px",
        marginBottom: "30px"
      }}>
        <h2>Analyze Logs</h2>

        <textarea
          rows="4"
          style={{ width: "100%" }}
          placeholder="Paste logs..."
          value={log}
          onChange={(e) => setLog(e.target.value)}
        />

        <br /><br />

        <input type="file" onChange={(e) => setFile(e.target.files[0])} />

        <br /><br />

        <button onClick={handleAnalyze}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>

      {/* ACTIONS */}
      <div style={{
        marginBottom: "20px",
        display: "flex",
        gap: "12px"
      }}>
        <button onClick={fetchIssues}>
          📂 Show Current Open Issues
        </button>

        {hasSelection() && (
          <button
            onClick={closeSelected}
            style={{
              background: "#ff4d4f",
              color: "white",
              border: "none",
              padding: "6px 12px",
              borderRadius: "6px"
            }}
          >
            ❌ Close Selected
          </button>
        )}
      </div>

      {/* GROUPED ISSUES */}
      {Object.keys(issues).map((group, i) => (
        <div key={i} style={{
          marginBottom: "20px",
          background: "#fff",
          padding: "15px",
          borderRadius: "10px"
        }}>
          <h2>📁 {group}</h2>

          {issues[group].map(issue => (
            <div key={issue.number} style={{
              marginBottom: "10px",
              padding: "10px",
              borderBottom: "1px solid #eee"
            }}>
              <input
                type="checkbox"
                checked={selected[issue.number] || false}
                onChange={() => toggleSelect(issue.number)}
              />

              <a
                href={issue.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ marginLeft: "10px" }}
              >
                {issue.title}
              </a>
            </div>
          ))}

        </div>
      ))}

    </div>
  );
}

export default App;