const FEATURES = [
  {
    title: 'Fact-checked claims',
    description:
      'Specific, checkable claims are pulled from the transcript and verified against a curated source corpus — never a guess without evidence.',
  },
  {
    title: 'Manipulation patterns',
    description:
      'Fast cuts, dramatic volume swings, rushed narration, and clickbait phrasing are measured directly, not guessed at.',
  },
  {
    title: 'One explainable score',
    description:
      'Every signal is combined with a documented, weighted formula into a single 0–100 score — with the reasoning always shown.',
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
      <div className="grid gap-6 sm:grid-cols-3">
        {FEATURES.map((feature) => (
          <div
            key={feature.title}
            className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-shadow duration-200 hover:shadow-md"
          >
            <h3 className="mb-2 text-sm font-semibold text-slate-900">{feature.title}</h3>
            <p className="text-sm leading-relaxed text-slate-500">{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
