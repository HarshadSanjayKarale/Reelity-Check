const CATEGORY_LABELS = {
  salary_career: 'Salary / Career',
  health: 'Health',
  finance: 'Finance',
  statistic: 'Statistic',
  other: 'Other',
};

const VERDICT_STYLES = {
  supported: { label: 'Supported', className: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20' },
  contradicted: { label: 'Contradicted', className: 'bg-red-50 text-red-700 ring-1 ring-red-600/20' },
  insufficient_evidence: {
    label: 'Insufficient evidence',
    className: 'bg-slate-100 text-slate-600 ring-1 ring-slate-400/20',
  },
};

export default function ClaimCard({ claim }) {
  const verdict = VERDICT_STYLES[claim.verification?.verdict] ?? null;

  return (
    <li className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition-shadow duration-200 hover:shadow-md">
      <div className="flex justify-between gap-3">
        <span className="text-sm text-slate-800">{claim.text}</span>
        <span className="h-fit shrink-0 rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700 ring-1 ring-indigo-600/20">
          {CATEGORY_LABELS[claim.category] ?? claim.category}
        </span>
      </div>

      {claim.verification && (
        <div className="mt-2.5 space-y-1.5">
          {verdict && (
            <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${verdict.className}`}>
              {verdict.label}
            </span>
          )}
          <p className="text-xs text-slate-500">{claim.verification.explanation}</p>
          {claim.verification.sources.length > 0 && (
            <ul className="list-inside list-disc space-y-0.5 text-xs text-slate-400">
              {claim.verification.sources.map((src) => (
                <li key={src}>
                  <a href={src} target="_blank" rel="noreferrer" className="underline hover:text-slate-600">
                    {src}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </li>
  );
}
