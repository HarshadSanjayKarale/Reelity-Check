export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/75 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-4 sm:px-6">
        <a href="#top" className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 via-violet-600 to-fuchsia-500 shadow-md shadow-indigo-500/30">
            <svg viewBox="0 0 24 24" className="h-5 w-5 text-white" fill="none">
              <path
                d="M8 12.5l2.8 2.8L16.5 9"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </span>
          <span className="text-lg font-semibold tracking-tight text-slate-900">
            Reel{' '}
            <span className="bg-gradient-to-r from-indigo-600 to-fuchsia-500 bg-clip-text text-transparent">
              Reality Check
            </span>
          </span>
        </a>

        <nav className="hidden items-center gap-6 text-sm font-medium text-slate-600 sm:flex">
          <a href="#how-it-works" className="transition-colors hover:text-slate-900">
            How it works
          </a>
          <a
            href="#analyze"
            className="rounded-full bg-slate-900 px-4 py-2 text-white transition-colors hover:bg-slate-700"
          >
            Analyze a reel
          </a>
        </nav>
      </div>
    </header>
  );
}
