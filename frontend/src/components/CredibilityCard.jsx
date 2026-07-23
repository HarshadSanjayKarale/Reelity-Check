import ScoreGauge from './ScoreGauge';

export default function CredibilityCard({ credibility }) {
  return (
    <div className="animate-fade-in rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start">
        <ScoreGauge score={credibility.credibility_score} />
        <div className="flex-1 text-center sm:text-left">
          <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-slate-400">
            Credibility score
          </h2>
          <p className="text-sm text-slate-700">{credibility.summary}</p>
          <div className="mt-4 space-y-2">
            {credibility.components.map((c) => (
              <div key={c.label} className="flex items-center justify-between text-xs">
                <span className="text-slate-500">
                  {c.label} <span className="text-slate-400">({Math.round(c.weight * 100)}% weight)</span>
                </span>
                <span className="font-medium text-slate-700">{Math.round(c.score)}/100</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
