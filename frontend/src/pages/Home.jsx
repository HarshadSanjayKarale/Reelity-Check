import { useEffect, useRef, useState } from 'react';
import { createReel, getReel } from '../api/reels';

const STATUS_LABELS = {
  pending: 'Queued…',
  downloading: 'Downloading video…',
  extracting: 'Extracting audio & frames…',
  transcribing: 'Transcribing audio…',
  extracting_claims: 'Extracting claims…',
  ready: 'Done',
  failed: 'Failed',
};

const CATEGORY_LABELS = {
  salary_career: 'Salary / Career',
  health: 'Health',
  finance: 'Finance',
  statistic: 'Statistic',
  other: 'Other',
};

export default function Home() {
  const [url, setUrl] = useState('');
  const [reel, setReel] = useState(null);
  const [submitError, setSubmitError] = useState(null);
  const pollRef = useRef(null);

  useEffect(() => {
    return () => clearInterval(pollRef.current);
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitError(null);
    setReel(null);
    clearInterval(pollRef.current);

    try {
      const created = await createReel(url);
      setReel(created);

      pollRef.current = setInterval(async () => {
        try {
          const updated = await getReel(created.id);
          setReel(updated);
          if (updated.status === 'ready' || updated.status === 'failed') {
            clearInterval(pollRef.current);
          }
        } catch (err) {
          setSubmitError(err.message);
          clearInterval(pollRef.current);
        }
      }, 2000);
    } catch (err) {
      setSubmitError(err.message);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col items-center px-4 py-16">
      <div className="w-full max-w-xl">
        <h1 className="text-3xl font-semibold mb-1">Reel Reality Check</h1>
        <p className="text-slate-500 mb-8">
          Phase 2: transcript + extracted claims. No fact-checking or credibility
          score yet — that's Phase 3.
        </p>

        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="url"
            required
            placeholder="https://www.instagram.com/reel/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="flex-1 rounded-lg border border-slate-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          <button
            type="submit"
            className="rounded-lg bg-indigo-600 px-4 py-2 text-white font-medium hover:bg-indigo-700"
          >
            Analyze
          </button>
        </form>

        {submitError && (
          <p className="mt-4 text-red-600 text-sm">{submitError}</p>
        )}

        {reel && (
          <div className="mt-8 rounded-lg border border-slate-200 bg-white p-5 space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-medium">{STATUS_LABELS[reel.status] ?? reel.status}</span>
              <span className="text-xs uppercase tracking-wide text-slate-400">
                {reel.platform}
              </span>
            </div>

            {reel.status === 'failed' && (
              <p className="text-red-600 text-sm">{reel.error}</p>
            )}

            {reel.transcript && (
              <div>
                <h2 className="text-sm font-semibold text-slate-700 mb-1">Transcript</h2>
                <p className="text-sm text-slate-600 max-h-40 overflow-y-auto whitespace-pre-wrap">
                  {reel.transcript || '(no speech detected)'}
                </p>
              </div>
            )}

            {reel.status === 'ready' && (
              <div>
                <h2 className="text-sm font-semibold text-slate-700 mb-2">
                  Extracted claims {reel.claims.length === 0 && '(none found)'}
                </h2>
                <ul className="space-y-2">
                  {reel.claims.map((claim, i) => (
                    <li
                      key={i}
                      className="text-sm rounded-md border border-slate-200 p-2 flex justify-between gap-3"
                    >
                      <span>{claim.text}</span>
                      <span className="shrink-0 text-xs rounded-full bg-indigo-50 text-indigo-700 px-2 py-0.5 h-fit">
                        {CATEGORY_LABELS[claim.category] ?? claim.category}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
