import ScoreBar from './ScoreBar';

export default function ManipulationPanel({ signals }) {
  return (
    <div className="animate-fade-in rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-400">
        Manipulation patterns
      </h2>
      <div className="mb-4 space-y-3">
        <ScoreBar label="Pacing (cuts)" value={signals.pacing_score} />
        <ScoreBar label="Tone (volume/urgency)" value={signals.tone_score} />
        <ScoreBar label="Clickbait text" value={signals.clickbait_score} />
      </div>
      <ul className="list-inside list-disc space-y-1 text-xs text-slate-500">
        {signals.notes.map((note, i) => (
          <li key={i}>{note}</li>
        ))}
      </ul>
    </div>
  );
}
