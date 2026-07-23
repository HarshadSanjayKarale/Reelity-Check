export default function AuthenticityPanel({ signal }) {
  return (
    <div className="animate-fade-in rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="mb-1 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
        Authenticity check
        <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium normal-case tracking-normal text-slate-500">
          minor signal
        </span>
      </h2>
      <p className="text-xs leading-relaxed text-slate-500">{signal.note}</p>
    </div>
  );
}
