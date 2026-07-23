const STEPS = [
  { key: 'downloading', label: 'Download' },
  { key: 'extracting', label: 'Extract' },
  { key: 'transcribing', label: 'Transcribe' },
  { key: 'extracting_claims', label: 'Claims' },
  { key: 'verifying_claims', label: 'Fact-check' },
  { key: 'detecting_manipulation', label: 'Manipulation' },
  { key: 'checking_authenticity', label: 'Authenticity' },
];

function stepState(status, index) {
  if (status === 'ready') return 'done';
  if (status === 'failed') return 'pending';
  if (status === 'pending') return index === 0 ? 'active' : 'pending';

  const activeIndex = STEPS.findIndex((s) => s.key === status);
  if (activeIndex === -1) return 'pending';
  if (index < activeIndex) return 'done';
  if (index === activeIndex) return 'active';
  return 'pending';
}

function StepIcon({ state }) {
  if (state === 'done') {
    return (
      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500 text-white shadow-sm">
        <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none">
          <path
            d="M6 12.5l3.8 3.8L18 8"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </span>
    );
  }
  if (state === 'active') {
    return (
      <span className="relative flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 text-white shadow-sm">
        <span className="absolute inset-0 rounded-full border-2 border-indigo-300 border-t-transparent animate-spin-slow" />
        <span className="h-2 w-2 rounded-full bg-white" />
      </span>
    );
  }
  return <span className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200 text-slate-400" />;
}

export default function PipelineLoader({ status }) {
  return (
    <div className="flex items-start">
      {STEPS.map((step, i) => {
        const state = stepState(status, i);
        return (
          <div key={step.key} className="flex flex-1 flex-col items-center">
            <div className="flex w-full items-center">
              <div className={`h-0.5 flex-1 ${i === 0 ? 'opacity-0' : state === 'pending' ? 'bg-slate-200' : 'bg-emerald-400'}`} />
              <StepIcon state={state} />
              <div
                className={`h-0.5 flex-1 ${
                  i === STEPS.length - 1 ? 'opacity-0' : state === 'done' ? 'bg-emerald-400' : 'bg-slate-200'
                }`}
              />
            </div>
            <span className="mt-1.5 text-center text-[11px] font-medium text-slate-500">{step.label}</span>
          </div>
        );
      })}
    </div>
  );
}
