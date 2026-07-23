export default function TranscriptPanel({ transcript }) {
  return (
    <div className="animate-fade-in rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-400">Transcript</h2>
      <p className="max-h-40 overflow-y-auto whitespace-pre-wrap text-sm leading-relaxed text-slate-600">
        {transcript || '(no speech detected)'}
      </p>
    </div>
  );
}
