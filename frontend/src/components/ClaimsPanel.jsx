import ClaimCard from './ClaimCard';

export default function ClaimsPanel({ claims }) {
  return (
    <div className="animate-fade-in rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-400">
        Extracted claims{' '}
        {claims.length === 0 && <span className="font-normal normal-case text-slate-400">(none found)</span>}
      </h2>
      <ul className="space-y-2">
        {claims.map((claim, i) => (
          <ClaimCard key={i} claim={claim} />
        ))}
      </ul>
    </div>
  );
}
