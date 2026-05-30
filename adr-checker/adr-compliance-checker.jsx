import { useState, useRef } from "react";

const RULES = [
  { id: "R01", category: "Structure", severity: "mandatory", description: "The ADR must have a clearly identified title that summarises the decision." },
  { id: "R02", category: "Structure", severity: "mandatory", description: "The ADR must state the problem context or the question being decided." },
  { id: "R03", category: "Structure", severity: "mandatory", description: "The ADR must document the decision that was made, stated as an affirmative action." },
  { id: "R04", category: "Structure", severity: "mandatory", description: "The ADR must include a status field (e.g. Proposed, Accepted, Deprecated, Superseded)." },
  { id: "R05", category: "Reasoning", severity: "mandatory", description: "The ADR must document the rationale or justification behind the decision." },
  { id: "R06", category: "Reasoning", severity: "advisory", description: "The ADR should document alternatives that were considered and why they were rejected." },
  { id: "R07", category: "Reasoning", severity: "advisory", description: "The ADR should identify assumptions that underpin the decision." },
  { id: "R08", category: "Consequences", severity: "mandatory", description: "The ADR must document consequences or implications of the decision, including trade-offs." },
  { id: "R09", category: "Consequences", severity: "advisory", description: "The ADR should identify risks introduced by the decision." },
  { id: "R10", category: "Traceability", severity: "advisory", description: "The ADR should reference related ADRs, requirements, or constraints that influenced the decision." },
  { id: "R11", category: "Traceability", severity: "mandatory", description: "The ADR must be attributable — it should identify who made or owns the decision." },
  { id: "R12", category: "Clarity", severity: "advisory", description: "The ADR should be written so that someone unfamiliar with the programme context can understand the decision and its rationale." },
];

const SAMPLE_ADR = `# ADR-042: Use Event-Driven Integration for Engine Health Data

Status: Accepted
Author: P. Marsh, Enterprise Architecture

## Context
The PPS digital backbone requires engine health telemetry from multiple sources to be available to the TotalCare analytics platform. Currently data flows via batch file transfer which introduces latency of up to 6 hours. The programme requires near-real-time visibility for predictive maintenance decisions.

## Decision
We will adopt an event-driven integration pattern using a message broker (Apache Kafka) to stream engine health data from sensor aggregators to the analytics platform.

## Rationale
Event-driven integration reduces latency from hours to seconds. Kafka is already provisioned within the programme data infrastructure, minimising new dependencies. The pattern decouples producers and consumers, allowing the analytics platform to evolve independently of sensor systems.

## Alternatives Considered
- **Polling API**: Rejected due to latency and load characteristics at scale.
- **Continued batch transfer**: Rejected as it does not meet the near-real-time requirement.
- **GraphQL subscriptions**: Considered but deprioritised due to team capability gap and lack of existing infrastructure.

## Consequences
- Consumers must handle out-of-order and duplicate events (at-least-once delivery).
- Operational complexity increases — Kafka cluster requires monitoring and management.
- Enables future analytics consumers to subscribe without upstream changes.
- Trade-off: higher operational overhead in exchange for latency and decoupling benefits.

## Risks
- Kafka operational expertise is currently limited within the programme team. Mitigation: training and knowledge transfer from platform team scheduled for Q3.
`;

const STATUS_COLORS = {
  pass: { bg: "#d1fae5", text: "#065f46", border: "#6ee7b7" },
  fail: { bg: "#fee2e2", text: "#991b1b", border: "#fca5a5" },
  partial: { bg: "#fef3c7", text: "#92400e", border: "#fcd34d" },
  not_applicable: { bg: "#f3f4f6", text: "#6b7280", border: "#d1d5db" },
  pending: { bg: "#f9fafb", text: "#9ca3af", border: "#e5e7eb" },
  running: { bg: "#eff6ff", text: "#1d4ed8", border: "#93c5fd" },
};

const SEVERITY_BADGE = {
  mandatory: { bg: "#fef2f2", text: "#dc2626" },
  advisory: { bg: "#f0fdf4", text: "#16a34a" },
};

const CATEGORY_COLORS = {
  Structure: "#6366f1",
  Reasoning: "#f59e0b",
  Consequences: "#ef4444",
  Traceability: "#10b981",
  Clarity: "#8b5cf6",
};

function StatusBadge({ status }) {
  const c = STATUS_COLORS[status] || STATUS_COLORS.pending;
  const labels = {
    pass: "✓ Pass",
    fail: "✗ Fail",
    partial: "◑ Partial",
    not_applicable: "— N/A",
    pending: "·· Pending",
    running: "⟳ Checking",
  };
  return (
    <span style={{
      padding: "2px 10px", borderRadius: 12, fontSize: 12, fontWeight: 600,
      background: c.bg, color: c.text, border: `1px solid ${c.border}`,
      fontFamily: "monospace", whiteSpace: "nowrap"
    }}>
      {labels[status] || status}
    </span>
  );
}

function RuleRow({ rule, result }) {
  const [expanded, setExpanded] = useState(false);
  const status = result?.status || "pending";
  const catColor = CATEGORY_COLORS[rule.category] || "#888";
  const sevBadge = SEVERITY_BADGE[rule.severity];

  return (
    <div style={{
      border: "1px solid #e5e7eb", borderRadius: 8, marginBottom: 8,
      background: status === "running" ? "#eff6ff" : "white",
      transition: "background 0.3s"
    }}>
      <div
        onClick={() => result && setExpanded(!expanded)}
        style={{
          display: "flex", alignItems: "center", gap: 10, padding: "10px 14px",
          cursor: result ? "pointer" : "default",
        }}
      >
        <span style={{
          fontFamily: "monospace", fontSize: 11, fontWeight: 700,
          color: catColor, minWidth: 36
        }}>{rule.id}</span>
        <span style={{
          fontSize: 11, padding: "1px 7px", borderRadius: 10, fontWeight: 600,
          background: catColor + "18", color: catColor, minWidth: 80, textAlign: "center"
        }}>{rule.category}</span>
        <span style={{
          fontSize: 11, padding: "1px 7px", borderRadius: 10, fontWeight: 600,
          background: sevBadge.bg, color: sevBadge.text, minWidth: 68, textAlign: "center"
        }}>{rule.severity}</span>
        <span style={{ flex: 1, fontSize: 13, color: "#374151" }}>{rule.description}</span>
        <StatusBadge status={status} />
        {result && <span style={{ color: "#9ca3af", fontSize: 12 }}>{expanded ? "▲" : "▼"}</span>}
      </div>
      {expanded && result && (
        <div style={{
          borderTop: "1px solid #f3f4f6", padding: "10px 14px 12px",
          background: "#fafafa", borderRadius: "0 0 8px 8px"
        }}>
          {result.evidence && (
            <div style={{ marginBottom: 8 }}>
              <span style={{ fontSize: 11, fontWeight: 700, color: "#6b7280", textTransform: "uppercase" }}>Evidence</span>
              <div style={{
                marginTop: 4, padding: "6px 10px", background: "#f3f4f6",
                borderRadius: 6, fontFamily: "monospace", fontSize: 12,
                color: "#374151", borderLeft: `3px solid ${catColor}`
              }}>{result.evidence}</div>
            </div>
          )}
          {result.explanation && (
            <div>
              <span style={{ fontSize: 11, fontWeight: 700, color: "#6b7280", textTransform: "uppercase" }}>Explanation</span>
              <div style={{ marginTop: 4, fontSize: 13, color: "#374151", lineHeight: 1.5 }}>{result.explanation}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SummaryBar({ results }) {
  const counts = { pass: 0, fail: 0, partial: 0, not_applicable: 0 };
  results.forEach(r => { if (r && counts[r.status] !== undefined) counts[r.status]++; });
  const total = results.filter(Boolean).length;
  if (total === 0) return null;

  const mandatoryFails = RULES.filter((r, i) =>
    r.severity === "mandatory" && results[i]?.status === "fail"
  ).length;

  return (
    <div style={{
      background: "white", border: "1px solid #e5e7eb", borderRadius: 10,
      padding: "14px 18px", marginBottom: 16
    }}>
      <div style={{ display: "flex", gap: 20, flexWrap: "wrap", alignItems: "center" }}>
        {Object.entries(counts).map(([s, n]) => (
          <div key={s} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <StatusBadge status={s} />
            <span style={{ fontSize: 18, fontWeight: 700, color: "#111" }}>{n}</span>
          </div>
        ))}
        <div style={{ marginLeft: "auto", fontSize: 13, color: "#6b7280" }}>
          {total} / {RULES.length} rules checked
        </div>
      </div>
      {mandatoryFails > 0 && (
        <div style={{
          marginTop: 10, padding: "6px 12px", background: "#fee2e2",
          borderRadius: 6, color: "#991b1b", fontSize: 13, fontWeight: 600
        }}>
          ⚠ {mandatoryFails} mandatory rule{mandatoryFails > 1 ? "s" : ""} failed — document does not meet minimum quality threshold.
        </div>
      )}
      {mandatoryFails === 0 && total === RULES.length && (
        <div style={{
          marginTop: 10, padding: "6px 12px", background: "#d1fae5",
          borderRadius: 6, color: "#065f46", fontSize: 13, fontWeight: 600
        }}>
          ✓ All mandatory rules passed.
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [document, setDocument] = useState(SAMPLE_ADR);
  const [results, setResults] = useState(Array(RULES.length).fill(null));
  const [running, setRunning] = useState(false);
  const [currentRule, setCurrentRule] = useState(null);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState("input"); // input | results
  const abortRef = useRef(false);

  async function checkRule(doc, rule) {
    const prompt = `You are a document quality checker evaluating an Architecture Decision Record (ADR).

DOCUMENT:
${doc}

RULE TO EVALUATE:
${rule.id} — ${rule.description}

Evaluate whether the document complies with this rule.
Respond ONLY with a JSON object, no preamble, no markdown fences:
{
  "rule_id": "${rule.id}",
  "status": "pass" or "fail" or "partial" or "not_applicable",
  "evidence": "a short direct quote or reference from the document supporting your assessment, or empty string if not applicable",
  "explanation": "one concise sentence explaining your assessment"
}`;

    const response = await fetch("/api/anthropic/v1/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "claude-sonnet-4-6",
        max_tokens: 1000,
        messages: [{ role: "user", content: prompt }],
      }),
    });

    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(`API error ${response.status}: ${body?.error?.message ?? response.statusText}`);
    }
    const data = await response.json();
    const text = data.content.map(b => b.text || "").join("").trim();
    const clean = text.replace(/```json|```/g, "").trim();
    return JSON.parse(clean);
  }

  async function runHarness() {
    if (!document.trim()) return;
    abortRef.current = false;
    setRunning(true);
    setError(null);
    setResults(Array(RULES.length).fill(null));
    setMode("results");

    // Process in thematic batches but sequentially within batch
    // Batches: Structure (R01-R04), Reasoning (R05-R07), Consequences (R08-R09), Traceability+Clarity (R10-R12)
    for (let i = 0; i < RULES.length; i++) {
      if (abortRef.current) break;

      setCurrentRule(RULES[i].id);

      // Mark as running
      setResults(prev => {
        const next = [...prev];
        next[i] = { status: "running" };
        return next;
      });

      try {
        const result = await checkRule(document, RULES[i]);
        setResults(prev => {
          const next = [...prev];
          next[i] = result;
          return next;
        });
      } catch (e) {
        setResults(prev => {
          const next = [...prev];
          next[i] = { status: "fail", evidence: "", explanation: `Check failed: ${e.message}` };
          return next;
        });
        if (e.message.includes("API error")) {
          setError(`API error — ${e.message}`);
          break;
        }
      }
    }

    setCurrentRule(null);
    setRunning(false);
  }

  function stop() {
    abortRef.current = true;
  }

  function reset() {
    abortRef.current = true;
    setResults(Array(RULES.length).fill(null));
    setCurrentRule(null);
    setRunning(false);
    setMode("input");
    setError(null);
  }

  const completedResults = results.filter(Boolean).filter(r => r.status !== "running");

  return (
    <div style={{
      minHeight: "100vh",
      background: "#f8fafc",
      fontFamily: "'IBM Plex Sans', 'Helvetica Neue', sans-serif",
    }}>
      {/* Header */}
      <div style={{
        background: "#0f172a", color: "white",
        padding: "16px 24px", display: "flex", alignItems: "center", gap: 14
      }}>
        <div style={{
          width: 36, height: 36, background: "#3b82f6", borderRadius: 8,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 18
        }}>⚖</div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 16, letterSpacing: "-0.3px" }}>ADR Compliance Checker</div>
          <div style={{ fontSize: 12, color: "#94a3b8" }}>Harness-driven rule-by-rule evaluation</div>
        </div>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          {mode === "results" && (
            <button onClick={reset} style={{
              padding: "6px 14px", borderRadius: 6, border: "1px solid #475569",
              background: "transparent", color: "#cbd5e1", cursor: "pointer", fontSize: 13
            }}>← New document</button>
          )}
          {running && (
            <button onClick={stop} style={{
              padding: "6px 14px", borderRadius: 6, border: "none",
              background: "#ef4444", color: "white", cursor: "pointer", fontSize: 13, fontWeight: 600
            }}>Stop</button>
          )}
        </div>
      </div>

      <div style={{ maxWidth: 900, margin: "0 auto", padding: "24px 16px" }}>

        {/* Input mode */}
        {mode === "input" && (
          <div>
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontWeight: 700, fontSize: 15, color: "#0f172a", marginBottom: 4 }}>
                Document to check
              </div>
              <div style={{ fontSize: 13, color: "#64748b" }}>
                Paste an Architecture Decision Record. A sample ADR is pre-loaded.
              </div>
            </div>
            <textarea
              value={document}
              onChange={e => setDocument(e.target.value)}
              style={{
                width: "100%", height: 320, padding: 14,
                borderRadius: 8, border: "1px solid #e2e8f0",
                fontFamily: "monospace", fontSize: 13, lineHeight: 1.6,
                resize: "vertical", background: "white", color: "#1e293b",
                boxSizing: "border-box"
              }}
            />

            {/* Rule set preview */}
            <div style={{ marginTop: 20, marginBottom: 16 }}>
              <div style={{ fontWeight: 700, fontSize: 15, color: "#0f172a", marginBottom: 10 }}>
                Quality rules ({RULES.length})
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {Object.entries(CATEGORY_COLORS).map(([cat, color]) => {
                  const catRules = RULES.filter(r => r.category === cat);
                  return (
                    <div key={cat} style={{
                      padding: "4px 12px", borderRadius: 20, fontSize: 12, fontWeight: 600,
                      background: color + "15", color: color, border: `1px solid ${color}40`
                    }}>
                      {cat} ({catRules.length})
                    </div>
                  );
                })}
              </div>
            </div>

            <button
              onClick={runHarness}
              disabled={!document.trim()}
              style={{
                padding: "10px 28px", borderRadius: 8, border: "none",
                background: document.trim() ? "#3b82f6" : "#94a3b8",
                color: "white", fontSize: 14, fontWeight: 700,
                cursor: document.trim() ? "pointer" : "not-allowed",
                letterSpacing: "-0.2px"
              }}
            >
              Run compliance check →
            </button>
          </div>
        )}

        {/* Results mode */}
        {mode === "results" && (
          <div>
            {running && (
              <div style={{
                background: "#eff6ff", border: "1px solid #bfdbfe",
                borderRadius: 8, padding: "10px 16px", marginBottom: 16,
                fontSize: 13, color: "#1d4ed8", display: "flex", alignItems: "center", gap: 8
              }}>
                <span style={{ animation: "spin 1s linear infinite", display: "inline-block" }}>⟳</span>
                Harness running — evaluating rule {currentRule}…
                <span style={{ color: "#64748b", marginLeft: "auto" }}>
                  {completedResults.length} / {RULES.length} complete
                </span>
              </div>
            )}

            {error && (
              <div style={{
                background: "#fee2e2", border: "1px solid #fca5a5",
                borderRadius: 8, padding: "10px 16px", marginBottom: 16,
                fontSize: 13, color: "#991b1b"
              }}>{error}</div>
            )}

            <SummaryBar results={results} />

            {/* Group by category */}
            {Object.entries(CATEGORY_COLORS).map(([category, color]) => {
              const catRules = RULES.filter(r => r.category === category);
              return (
                <div key={category} style={{ marginBottom: 20 }}>
                  <div style={{
                    display: "flex", alignItems: "center", gap: 8, marginBottom: 10
                  }}>
                    <div style={{
                      width: 4, height: 18, borderRadius: 2, background: color
                    }} />
                    <span style={{ fontWeight: 700, fontSize: 14, color: "#0f172a" }}>{category}</span>
                    <span style={{ fontSize: 12, color: "#94a3b8" }}>
                      {catRules.length} rule{catRules.length > 1 ? "s" : ""}
                    </span>
                  </div>
                  {catRules.map(rule => {
                    const idx = RULES.findIndex(r => r.id === rule.id);
                    return <RuleRow key={rule.id} rule={rule} result={results[idx]} />;
                  })}
                </div>
              );
            })}
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
