import type { ReactNode } from 'react';

export function AuthShell({
  title,
  description,
  children,
  mascotImage = '/mascot/mascot-welcome.jpg',
  badgeText = 'Automated Review & Code Lessons',
}: {
  title: string;
  description?: ReactNode;
  children: ReactNode;
  mascotImage?: string;
  badgeText?: string;
}) {
  return (
    <main className="auth-page">
      <div className="auth-box">
        <div className="auth-brand">
          <img src="/mascot/mascot-logo.png" alt="CodeGate Mascot" className="w-9 h-9 rounded-xl shadow-md object-cover" />
          <span>CodeGate</span>
          <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700">Beta</span>
        </div>

        {mascotImage && (
          <div className="relative inline-block mb-3">
            <img src={mascotImage} alt="Mascot greeting" className="auth-mascot" />
            <div className="absolute -bottom-1 -right-1 bg-white rounded-full p-1 shadow-md border border-slate-100">
              <span className="block w-3.5 h-3.5 rounded-full bg-emerald-500 ring-2 ring-white"></span>
            </div>
          </div>
        )}

        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100/80 text-indigo-700 text-xs font-semibold mb-3">
          <span>🎓</span> {badgeText}
        </div>

        <h1>{title}</h1>
        {description && <div className="text-slate-500 text-sm max-w-sm mx-auto leading-relaxed">{description}</div>}

        <div className="auth-panel">{children}</div>

        <div className="mt-8 flex items-center justify-center gap-6 text-xs text-slate-400 font-medium">
          <span>Clean Code Guardrails</span>
          <span>•</span>
          <span>Interactive Student Feedback</span>
          <span>•</span>
          <span>GitHub Synced</span>
        </div>
      </div>
    </main>
  );
}
