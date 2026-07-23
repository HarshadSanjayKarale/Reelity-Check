import { useEffect, useRef, useState } from 'react';
import { createReel, getReel } from '../api/reels';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import HowItWorks from '../components/HowItWorks';
import PipelineLoader from '../components/PipelineLoader';
import CredibilityCard from '../components/CredibilityCard';
import TranscriptPanel from '../components/TranscriptPanel';
import ClaimsPanel from '../components/ClaimsPanel';
import ManipulationPanel from '../components/ManipulationPanel';
import AuthenticityPanel from '../components/AuthenticityPanel';

const STATUS_LABELS = {
  pending: 'Queued…',
  downloading: 'Downloading video…',
  extracting: 'Extracting audio & frames…',
  transcribing: 'Transcribing audio…',
  extracting_claims: 'Extracting claims…',
  verifying_claims: 'Fact-checking claims…',
  detecting_manipulation: 'Analyzing pacing & tone…',
  checking_authenticity: 'Checking authenticity…',
  ready: 'Done',
  failed: 'Failed',
};

export default function Home() {
  const [url, setUrl] = useState('');
  const [reel, setReel] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const pollRef = useRef(null);
  const resultsRef = useRef(null);

  useEffect(() => {
    return () => clearInterval(pollRef.current);
  }, []);

  // Scroll into view once when a new analysis starts (reel flips null -> truthy),
  // not on every polling update — hence depending on the boolean, not reel itself.
  useEffect(() => {
    if (reel) {
      resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [reel === null]);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitError(null);
    setReel(null);
    clearInterval(pollRef.current);
    setSubmitting(true);

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
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div id="top" className="min-h-screen bg-slate-50">
      <Navbar />
      <Hero url={url} setUrl={setUrl} onSubmit={handleSubmit} submitting={submitting} />
      <HowItWorks />

      <div ref={resultsRef} className="mx-auto max-w-3xl scroll-mt-20 px-4 pb-24 sm:px-6">
        {submitError && (
          <p className="animate-fade-in rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600 ring-1 ring-red-600/10">
            {submitError}
          </p>
        )}

        {reel && (
          <div className="space-y-5">
            <div className="animate-fade-in rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <span className="text-sm font-medium text-slate-700">
                  {STATUS_LABELS[reel.status] ?? reel.status}
                </span>
                <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  {reel.platform}
                </span>
              </div>

              {reel.status !== 'failed' && <PipelineLoader status={reel.status} />}

              {reel.status === 'failed' && (
                <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{reel.error}</p>
              )}
            </div>

            {reel.status === 'ready' && reel.credibility && (
              <CredibilityCard credibility={reel.credibility} />
            )}

            {reel.transcript && <TranscriptPanel transcript={reel.transcript} />}

            {reel.status === 'ready' && <ClaimsPanel claims={reel.claims} />}

            {reel.status === 'ready' && reel.manipulation_signals && (
              <ManipulationPanel signals={reel.manipulation_signals} />
            )}

            {reel.status === 'ready' && reel.authenticity_signal && (
              <AuthenticityPanel signal={reel.authenticity_signal} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
