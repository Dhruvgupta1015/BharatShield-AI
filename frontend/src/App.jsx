import { useState, useEffect } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function App() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState(null);

  // Check backend health on page load
  useEffect(() => {
    checkHealth();
  }, []);

  // Check backend health on first click or on demand
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

    const healthy = await checkHealth();

    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: input }),
      });

      if (!response.ok) {
        throw new Error("Failed to analyze");
      }

      const data = await response.json();

      setResult({
        connected: healthy,
        riskLevel: data.risk_level,
        riskSignals: data.signals,
        explanation: data.explanation,
        action: data.recommended_actions.length > 0 ? data.recommended_actions.join(" ") : "No specific action required.",
      });
    } catch (error) {
      setResult({
        connected: healthy,
        riskLevel: "Error",
        riskSignals: [],
        explanation: "Unable to analyze. Please try again.",
        action: "Ensure the backend server is running.",
      });
    }

    setLoading(false);
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-bharat-600/50 bg-bharat-800/60 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ShieldIcon />
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white">
                BharatShield AI
              </h1>
              <p className="text-xs text-bharat-400 font-medium tracking-wide">
                Explainable Regional-Language Phishing Detection
              </p>
            </div>
          </div>
          <span className="hidden sm:inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full bg-saffron/10 text-saffron border border-saffron/20">
            <span className="w-1.5 h-1.5 rounded-full bg-saffron animate-pulse" />
            Foundation
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-6 py-10">
        {/* Input Section */}
        <section id="input-section" className="mb-8">
          <label
            htmlFor="message-input"
            className="block text-sm font-semibold text-bharat-300 mb-2"
          >
            Paste suspicious message, text, or URL
          </label>
          <textarea
            id="message-input"
            className="w-full h-40 bg-bharat-800 border border-bharat-600 rounded-xl px-4 py-3 text-sm text-white placeholder-bharat-400 resize-none focus:outline-none focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary transition-all duration-200"
            placeholder={"Example: \"Aapka account block ho jayega, turant click karein: http://amaz0n-verify.xyz/login\""}
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />

          <div className="mt-4 flex items-center gap-3">
            <button
              id="analyze-btn"
              onClick={handleAnalyze}
              disabled={loading || !input.trim()}
              className="px-6 py-2.5 bg-accent-primary hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-lg shadow-lg shadow-accent-glow transition-all duration-200 hover:shadow-xl hover:shadow-accent-glow active:scale-[0.98]"
            >
              {loading ? "Checking…" : "Analyze"}
            </button>
            <span className="text-xs text-bharat-400">
              Supports Hindi · English · Hinglish
            </span>
          </div>
        </section>

        {/* Result Section */}
        <section id="result-section">
          {result ? (
            <div className="bg-bharat-800/80 border border-bharat-600 rounded-xl overflow-hidden">
              {/* Result Header */}
              <div className="px-6 py-4 border-b border-bharat-600/50 flex items-center justify-between">
                <h2 className="text-sm font-semibold text-white">
                  Analysis Result
                </h2>
                <StatusBadge connected={result.connected} />
              </div>

              {/* Result Grid */}
              <div className="grid sm:grid-cols-2 gap-px bg-bharat-600/30">
                <ResultCard
                  label="Risk Level"
                  value={result.riskLevel}
                  icon="◆"
                />
                <ResultCard
                  label="Risk Signals"
                  value={
                    result.riskSignals.length > 0
                      ? result.riskSignals.join(", ")
                      : "None detected"
                  }
                  icon="⚡"
                />
                <ResultCard
                  label="Explanation"
                  value={result.explanation}
                  icon="💡"
                  full
                />
                <ResultCard
                  label="Recommended Action"
                  value={result.action}
                  icon="→"
                  full
                />
              </div>
            </div>
          ) : (
            <div className="border border-dashed border-bharat-600 rounded-xl px-6 py-12 text-center">
              <p className="text-bharat-400 text-sm">
                Paste a message above and click{" "}
                <span className="text-accent-primary font-medium">Analyze</span>{" "}
                to check for phishing risk.
              </p>
            </div>
          )}
        </section>

        {/* Backend Health Indicator */}
        {backendStatus && (
          <div className="mt-6 text-xs text-bharat-400 flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus.status === "ok"
                  ? "bg-risk-low"
                  : "bg-risk-high"
              }`}
            />
            Backend:{" "}
            {backendStatus.status === "ok"
              ? `Connected (${backendStatus.stage})`
              : "Unreachable — start the FastAPI server"}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-bharat-600/30 py-4 text-center text-xs text-bharat-500">
        BharatShield AI · Omnikon National Hackathon 2026 · Dhruv Gupta &amp; Vivek Pandey
      </footer>
    </div>
  );
}

/* ── Small sub-components ── */

function ShieldIcon() {
  return (
    <svg
      width="32"
      height="32"
      viewBox="0 0 32 32"
      fill="none"
      className="shrink-0"
    >
      <path
        d="M16 2L4 8v8c0 7.18 5.12 13.88 12 16 6.88-2.12 12-8.82 12-16V8L16 2z"
        fill="url(#shield-grad)"
        opacity="0.9"
      />
      <path
        d="M16 6l-8 4v6c0 5.06 3.58 9.78 8 11.28V6z"
        fill="#f97316"
        opacity="0.6"
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

function StatusBadge({ connected }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${
        connected
          ? "bg-risk-low/10 text-risk-low border border-risk-low/20"
          : "bg-risk-high/10 text-risk-high border border-risk-high/20"
      }`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          connected ? "bg-risk-low" : "bg-risk-high"
        }`}
      />
      {connected ? "Backend Connected" : "Backend Offline"}
    </span>
  );
}

function ResultCard({ label, value, icon, full }) {
  return (
    <div
      className={`bg-bharat-800 px-6 py-4 ${
        full ? "sm:col-span-2" : ""
      }`}
    >
      <div className="flex items-center gap-2 mb-1">
        <span className="text-xs">{icon}</span>
        <span className="text-xs font-semibold text-bharat-300 uppercase tracking-wider">
          {label}
        </span>
      </div>
      <p className="text-sm text-white/80 leading-relaxed">{value}</p>
    </div>
  );
}

export default App;
