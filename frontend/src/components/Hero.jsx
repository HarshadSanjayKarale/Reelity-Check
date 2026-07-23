export default function Hero({ url, setUrl, onSubmit, submitting }) {
  return (
    <section id="analyze" className="relative overflow-hidden bg-gradient-to-br from-indigo-700 via-violet-700 to-fuchsia-600">
      <div className="pointer-events-none absolute -left-24 -top-24 h-72 w-72 rounded-full bg-fuchsia-400/30 blur-3xl animate-blob" />
      <div
        className="pointer-events-none absolute -right-16 top-24 h-72 w-72 rounded-full bg-indigo-300/30 blur-3xl animate-blob"
        style={{ animationDelay: '2.5s' }}
      />

      <div className="relative mx-auto max-w-3xl px-6 py-20 text-center sm:py-28">
        <span className="mb-5 inline-block rounded-full bg-white/10 px-3 py-1 text-xs font-medium tracking-wide text-white/80 ring-1 ring-white/25">
          Multi-signal AI credibility check
        </span>
        <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
          Know what&rsquo;s real,
          <br />
          before you believe it
        </h1>
        <p className="mx-auto mb-10 mt-4 max-w-xl text-lg text-white/80">
          Paste a Reel or Short. We fact-check the claims, catch manipulative editing, and
          give you one explainable credibility score — not just a fake/real label.
        </p>

        <form onSubmit={onSubmit} className="mx-auto flex max-w-xl flex-col gap-3 sm:flex-row">
          <input
            type="url"
            required
            placeholder="https://www.instagram.com/reel/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="flex-1 rounded-full bg-white px-5 py-3.5 text-slate-900 placeholder:text-slate-400 shadow-lg outline-none ring-0 focus:ring-4 focus:ring-white/40"
          />
          <button
            type="submit"
            disabled={submitting}
            className="rounded-full bg-white px-7 py-3.5 font-semibold text-indigo-700 shadow-lg transition-all duration-150 hover:bg-white/90 active:scale-95 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting ? (
              <span className="flex items-center justify-center gap-2">
                <span className="h-4 w-4 animate-spin-slow rounded-full border-2 border-indigo-700/30 border-t-indigo-700" />
                Starting…
              </span>
            ) : (
              'Analyze'
            )}
          </button>
        </form>
      </div>
    </section>
  );
}
