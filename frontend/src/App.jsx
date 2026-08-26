import { useState, useEffect } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

/* ═══════════════════════════════════════════════════════════════════════
   Configuration Maps
   ═══════════════════════════════════════════════════════════════════════ */

const VERDICT_CONFIG = {
  HIGH_RISK: {
    label: "High Risk",
    icon: "🚨",
    bg: "from-red-950/80 via-red-900/40 to-bharat-800/80",
    border: "border-red-500/40",
    text: "text-red-400",
    badge: "bg-red-500/15 text-red-400 border border-red-500/30",
    scoreColor: "#ef4444",
    glow: "shadow-lg shadow-red-500/10",
  },
  SUSPICIOUS: {
    label: "Suspicious",
    icon: "⚠️",
    bg: "from-amber-950/80 via-amber-900/40 to-bharat-800/80",
    border: "border-amber-500/40",
    text: "text-amber-400",
    badge: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
    scoreColor: "#eab308",
    glow: "shadow-lg shadow-amber-500/10",
  },
  LOW_RISK: {
    label: "Low Risk",
    icon: "✅",
    bg: "from-emerald-950/80 via-emerald-900/40 to-bharat-800/80",
    border: "border-emerald-500/40",
    text: "text-emerald-400",
    badge: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
    scoreColor: "#22c55e",
    glow: "shadow-lg shadow-emerald-500/10",
  },
};

const SEVERITY_STYLES = {
  high: { dot: "bg-red-400", text: "text-red-400/80" },
  medium: { dot: "bg-amber-400", text: "text-amber-400/80" },
  low: { dot: "bg-blue-400", text: "text-blue-400/80" },
};

/* ═══════════════════════════════════════════════════════════════════════
   App Root
   ═══════════════════════════════════════════════════════════════════════ */

function App() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState(null);

  useEffect(() => {
    checkHealth();
  }, []);

  async function checkHealth() {
    try {
      const res = await fetch(`${API_BASE}/health`);
      const data = await res.json();
      setBackendStatus(data);
      return true;
    } catch {
      setBackendStatus({ status: "unreachable" });
      return false;
    }
  }

  async function handleAnalyze() {
    if (!input.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || "Analysis failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        verdict: "ERROR",
        risk_score: 0,
        confidence: 0,
        language: "Unknown",
        analysis_summary:
          error.message || "Unable to analyze. Please try again.",
        signals: [],
        url_analysis: [],
        ml_analysis: { available: false },
        recommended_actions: [
          "Ensure the backend server is running and try again.",
        ],
      });
    }

    setLoading(false);
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Header ── */}
      <header className="border-b border-bharat-600/50 bg-bharat-800/60 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4 sm:py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ShieldIcon />
            <div>
              <h1 className="text-lg sm:text-xl font-bold tracking-tight text-white">
                BharatShield AI
              </h1>
              <p className="text-[11px] sm:text-xs text-bharat-400 font-medium tracking-wide">
                Explainable Regional-Language Phishing Detection
              </p>
            </div>
          </div>
          <span className="hidden sm:inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full bg-accent-primary/10 text-accent-primary border border-accent-primary/20">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-primary animate-pulse" />
            Phase 2 MVP
          </span>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-10">
        {/* Input */}
        <section id="input-section" className="mb-8">
          <label
            htmlFor="message-input"
            className="block text-sm font-semibold text-bharat-300 mb-2"
          >
            Paste suspicious message, text, or URL
          </label>
          <textarea
            id="message-input"
            className="w-full h-32 sm:h-36 bg-bharat-800 border border-bharat-600 rounded-xl px-4 py-3 text-sm text-white placeholder-bharat-500 resize-none focus:outline-none focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary transition-all duration-200"
            placeholder={
              'Example: "Aapka account block ho jayega, turant click karein: http://amaz0n-verify.xyz/login"'
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleAnalyze();
              }
            }}
          />
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <button
              id="analyze-btn"
              onClick={handleAnalyze}
              disabled={loading || !input.trim()}
              className="px-5 sm:px-6 py-2.5 bg-accent-primary hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-lg shadow-lg shadow-accent-glow transition-all duration-200 hover:shadow-xl hover:shadow-accent-glow active:scale-[0.98]"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <Spinner /> Analyzing…
                </span>
              ) : (
                "🛡️ Analyze"
              )}
            </button>
            <span className="text-xs text-bharat-400">
              Supports Hindi · English · Hinglish
            </span>
          </div>
        </section>

        {/* Result */}
        <section id="result-section">
          {result ? (
            result.verdict === "ERROR" ? (
              <ErrorCard message={result.analysis_summary} />
            ) : (
              <AnalysisResult result={result} />
            )
          ) : (
            <EmptyState />
          )}
        </section>

        {/* Backend Health */}
        {backendStatus && (
          <div className="mt-6 text-xs text-bharat-400 flex flex-wrap items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus.status === "ok" ? "bg-risk-low" : "bg-risk-high"
              }`}
            />
            {backendStatus.status === "ok" ? (
              <>
                Backend Connected (v{backendStatus.version || "?"})
                {backendStatus.ml_model_loaded && (
                  <span className="text-emerald-400">· ML Model Active</span>
                )}
              </>
            ) : (
              "Backend Unreachable — start the FastAPI server"
            )}
          </div>
        )}
      </main>

      {/* ── Footer ── */}
      <footer className="border-t border-bharat-600/30 py-4 text-center text-xs text-bharat-500">
        BharatShield AI · Omnikon National Hackathon 2026 · Dhruv Gupta &amp;
        Vivek Pandey
      </footer>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════
   Analysis Result — Main Container
   ═══════════════════════════════════════════════════════════════════════ */

function AnalysisResult({ result }) {
  const v = VERDICT_CONFIG[result.verdict] || VERDICT_CONFIG.LOW_RISK;

  return (
    <div className="space-y-4 animate-in">
      {/* ── 1. Verdict Banner ── */}
      <div
        className={`rounded-xl border ${v.border} bg-gradient-to-r ${v.bg} p-5 sm:p-6 ${v.glow}`}
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          {/* Left: Verdict + Summary */}
          <div className="flex items-start gap-3 sm:gap-4 min-w-0">
            <span className="text-3xl sm:text-4xl shrink-0 pt-0.5">
              {v.icon}
            </span>
            <div className="min-w-0">
              <div className={`text-xl sm:text-2xl font-bold ${v.text}`}>
                {v.label}
              </div>
              <p className="text-sm text-bharat-300 mt-1 leading-relaxed">
                {result.analysis_summary}
              </p>
            </div>
          </div>

          {/* Right: Score ring + Language */}
          <div className="flex items-center gap-4 sm:gap-5 shrink-0 ml-11 sm:ml-0">
            <RiskScoreRing
              score={result.risk_score}
              color={v.scoreColor}
            />
            <div className="text-left sm:text-right">
              <div className="text-[10px] text-bharat-400 uppercase tracking-wider font-semibold">
                Language
              </div>
              <div className="text-sm text-white font-medium mt-0.5">
                {result.language}
              </div>
              <div className="text-[11px] text-bharat-500 mt-1">
                Confidence: {Math.round(result.confidence * 100)}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── 2. AI Classification ── */}
      {result.ml_analysis?.available && result.ml_analysis.prediction && (
        <div className="rounded-xl border border-bharat-600 bg-bharat-800/80 p-4 sm:p-5">
          <SectionHeader icon="🤖" title="AI Classification">
            {result.ml_analysis.model_version && (
              <span className="text-[10px] text-bharat-500 font-mono">
                Model {result.ml_analysis.model_version}
              </span>
            )}
          </SectionHeader>

          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mt-3">
            <span
              className={`inline-flex items-center self-start gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
                result.ml_analysis.prediction === "phishing"
                  ? "bg-red-500/15 text-red-400 border-red-500/30"
                  : "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
              }`}
            >
              {result.ml_analysis.prediction === "phishing"
                ? "⚠ Phishing Detected"
                : "✓ Likely Benign"}
            </span>

            {result.ml_analysis.confidence != null && (
              <div className="flex items-center gap-3">
                <span className="text-xs text-bharat-400">Confidence</span>
                <div className="w-24 h-2 bg-bharat-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      result.ml_analysis.prediction === "phishing"
                        ? "bg-red-400"
                        : "bg-emerald-400"
                    }`}
                    style={{
                      width: `${Math.round(
                        result.ml_analysis.confidence * 100
                      )}%`,
                    }}
                  />
                </div>
                <span className="text-xs text-white font-mono w-10 text-right">
                  {Math.round(result.ml_analysis.confidence * 100)}%
                </span>
              </div>
            )}
          </div>

          <p className="text-[11px] text-bharat-500 mt-3 leading-relaxed">
            English-dominant ML baseline · Hindi/Hinglish detection uses
            rule-based analysis
          </p>
        </div>
      )}

      {/* ── 3. Threat Signals ── */}
      {result.signals.length > 0 && (
        <div className="rounded-xl border border-bharat-600 bg-bharat-800/80 overflow-hidden">
          <div className="px-4 sm:px-5 py-3 border-b border-bharat-600/50 flex items-center justify-between">
            <SectionHeader icon="⚡" title="Why It Was Flagged" />
            <span className="text-xs text-bharat-400">
              {result.signals.length} signal
              {result.signals.length !== 1 ? "s" : ""}
            </span>
          </div>
          <div className="divide-y divide-bharat-600/30">
            {result.signals.map((signal) => (
              <SignalCard key={signal.id} signal={signal} />
            ))}
          </div>
        </div>
      )}

      {/* ── 4. URL Intelligence ── */}
      {result.url_analysis.length > 0 && (
        <div className="rounded-xl border border-bharat-600 bg-bharat-800/80 overflow-hidden">
          <div className="px-4 sm:px-5 py-3 border-b border-bharat-600/50 flex items-center justify-between">
            <SectionHeader icon="🔗" title="URL Intelligence" />
            <span className="text-xs text-bharat-400">
              {result.url_analysis.length} URL
              {result.url_analysis.length !== 1 ? "s" : ""} analyzed
            </span>
          </div>
          <div className="divide-y divide-bharat-600/30">
            {result.url_analysis.map((url, i) => (
              <UrlCard key={i} urlData={url} />
            ))}
          </div>
        </div>
      )}

      {/* ── 5. Recommended Actions ── */}
      <div className="rounded-xl border border-bharat-600 bg-bharat-800/80 overflow-hidden">
        <div className="px-4 sm:px-5 py-3 border-b border-bharat-600/50">
          <SectionHeader icon="🛡️" title="Recommended Actions" />
        </div>
        <div className="p-4 sm:p-5 space-y-3">
          {result.recommended_actions.map((action, i) => (
            <div key={i} className="flex items-start gap-3">
              <div className="mt-0.5 w-5 h-5 rounded-full bg-accent-primary/15 flex items-center justify-center shrink-0">
                <span className="text-accent-primary text-[10px] font-bold">
                  {i + 1}
                </span>
              </div>
              <p className="text-sm text-white/80 leading-relaxed">{action}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════
   Sub-Components
   ═══════════════════════════════════════════════════════════════════════ */

function RiskScoreRing({ score, color }) {
  const radius = 30;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative w-[72px] h-[72px] flex items-center justify-center shrink-0">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 72 72">
        <circle
          cx="36" cy="36" r={radius}
          fill="none" stroke="currentColor" strokeWidth="4"
          className="text-bharat-700"
        />
        <circle
          cx="36" cy="36" r={radius}
          fill="none" stroke={color} strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="score-ring-progress"
          style={{ "--circumference": circumference }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-lg font-bold text-white leading-none">{score}</span>
        <span className="text-[9px] text-bharat-400 uppercase tracking-wider mt-0.5">
          Risk
        </span>
      </div>
    </div>
  );
}

function SignalCard({ signal }) {
  const sev = SEVERITY_STYLES[signal.severity] || SEVERITY_STYLES.medium;

  return (
    <div className="px-4 sm:px-5 py-3 flex items-start gap-3 hover:bg-bharat-700/20 transition-colors">
      <div className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${sev.dot}`} />
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
          <span className="text-sm font-medium text-white">
            {signal.label}
          </span>
          <span
            className={`text-[10px] font-semibold uppercase tracking-wider ${sev.text}`}
          >
            {signal.severity}
          </span>
        </div>
        <p className="text-xs text-bharat-400 mt-0.5 leading-relaxed">
          {signal.description}
        </p>
      </div>
    </div>
  );
}

function UrlCard({ urlData }) {
  const hasRisk = urlData.flags.length > 0;

  return (
    <div className="px-4 sm:px-5 py-3.5">
      {/* URL display */}
      <div className="flex items-center gap-2 mb-2">
        <span
          className={`w-2 h-2 rounded-full shrink-0 ${
            hasRisk ? "bg-amber-400" : "bg-emerald-400"
          }`}
        />
        <code className="text-xs text-white font-mono break-all">
          {urlData.url}
        </code>
      </div>

      {/* Risk reasons */}
      {urlData.risk_reasons.length > 0 ? (
        <div className="ml-4 space-y-1">
          {urlData.risk_reasons.map((reason, i) => (
            <p
              key={i}
              className="text-xs text-bharat-400 flex items-start gap-2"
            >
              <span className="text-amber-500 shrink-0">›</span>
              {reason}
            </p>
          ))}
        </div>
      ) : (
        <p className="ml-4 text-xs text-bharat-500">
          No suspicious patterns detected in this URL.
        </p>
      )}

      {/* Tags */}
      <div className="ml-4 mt-2 flex flex-wrap gap-1.5">
        {urlData.scheme && (
          <Tag>{urlData.scheme.toUpperCase()}</Tag>
        )}
        {urlData.hostname && <Tag>{urlData.hostname}</Tag>}
        {urlData.is_shortened && <Tag variant="warn">Shortened</Tag>}
        {urlData.is_ip && <Tag variant="danger">IP Address</Tag>}
      </div>
    </div>
  );
}

function Tag({ children, variant }) {
  const styles = {
    warn: "bg-amber-500/15 text-amber-400 border-amber-500/20",
    danger: "bg-red-500/15 text-red-400 border-red-500/20",
  };
  const cls =
    styles[variant] || "bg-bharat-700 text-bharat-400 border-bharat-600/50";

  return (
    <span
      className={`text-[10px] px-2 py-0.5 rounded border font-mono ${cls}`}
    >
      {children}
    </span>
  );
}

function SectionHeader({ icon, title, children }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm">{icon}</span>
      <h3 className="text-xs font-semibold text-bharat-300 uppercase tracking-wider">
        {title}
      </h3>
      {children && <div className="ml-auto">{children}</div>}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="border border-dashed border-bharat-600 rounded-xl px-6 py-14 text-center">
      <div className="text-4xl mb-3">🛡️</div>
      <p className="text-bharat-400 text-sm">
        Paste a message above and click{" "}
        <span className="text-accent-primary font-medium">Analyze</span> to
        check for phishing risks.
      </p>
      <p className="text-bharat-500 text-xs mt-2">
        Works with English, Hindi, and Hinglish messages
      </p>
    </div>
  );
}

function ErrorCard({ message }) {
  return (
    <div className="rounded-xl border border-red-500/30 bg-red-950/30 p-6 text-center">
      <div className="text-3xl mb-2">⚠️</div>
      <p className="text-red-400 text-sm font-medium">{message}</p>
      <p className="text-bharat-400 text-xs mt-2">
        Ensure the backend server is running and try again.
      </p>
    </div>
  );
}

function Spinner() {
  return (
    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
      <circle
        className="opacity-25"
        cx="12" cy="12" r="10"
        stroke="currentColor" strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

function ShieldIcon() {
  return (
    <svg
      width="32" height="32" viewBox="0 0 32 32"
      fill="none" className="shrink-0"
    >
      <path
        d="M16 2L4 8v8c0 7.18 5.12 13.88 12 16 6.88-2.12 12-8.82 12-16V8L16 2z"
        fill="url(#shield-grad)" opacity="0.9"
      />
      <path
        d="M16 6l-8 4v6c0 5.06 3.58 9.78 8 11.28V6z"
        fill="#f97316" opacity="0.6"
      />
      <defs>
        <linearGradient id="shield-grad" x1="4" y1="2" x2="28" y2="26">
          <stop stopColor="#3b82f6" />
          <stop offset="1" stopColor="#1d4ed8" />
        </linearGradient>
      </defs>
    </svg>
  );
}

export default App;
