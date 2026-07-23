export default function ScoreBar({ label, value }) {
  const percent = Math.round(value * 100);
  const color = percent >= 60 ? 'bg-red-500' : percent >= 30 ? 'bg-amber-500' : 'bg-emerald-500';

  return (
    <div>
      <div className="mb-1 flex justify-between text-xs font-medium text-slate-500">
        <span>{label}</span>
        <span>{percent}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full rounded-full ${color} transition-all duration-700 ease-out`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
