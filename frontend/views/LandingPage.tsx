
import React from 'react';

interface LandingPageProps {
  onStart: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onStart }) => {
  return (
    <div className="h-full overflow-y-auto bg-white dark:bg-background-dark custom-scrollbar">
      {/* Navigation Bar */}
      <nav className="fixed top-0 left-0 right-0 h-20 bg-white/80 dark:bg-background-dark/80 backdrop-blur-md z-50 border-b border-slate-100 dark:border-border-dark px-8 md:px-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="size-10 bg-primary rounded-lg flex items-center justify-center text-white">
            <span className="material-symbols-outlined font-bold text-2xl">gavel</span>
          </div>
          <span className="text-xl font-black tracking-tighter">GAVEL</span>
        </div>
        <div className="flex items-center">
          <button 
            onClick={onStart}
            className="text-sm font-bold text-primary hover:text-primary-hover transition-colors"
          >
            Enter Dashboard
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-44 pb-24 px-8 md:px-16 max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div className="space-y-8 animate-in fade-in slide-in-from-left duration-700">
            <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-1.5 rounded-full border border-primary/20">
              <span className="material-symbols-outlined text-sm font-bold">verified</span>
              <span className="text-[10px] font-black uppercase tracking-widest">Enterprise Legal AI</span>
            </div>
            <h1 className="text-6xl md:text-7xl font-black leading-[1.05] tracking-tight">
              The Intelligent <br/>
              <span className="text-primary italic">Backbone</span> of <br/>
              Modern Law.
            </h1>
            <p className="text-xl text-slate-500 dark:text-text-secondary max-w-xl leading-relaxed">
              GAVEL (Generative AI for Virtual Evaluation and Legal Assistance) empowers legal teams with multimodal analysis, forensic verification, and multi-agent drafting workflows.
            </p>
            <div className="flex flex-wrap gap-4 pt-4">
              <button 
                onClick={onStart}
                className="bg-primary hover:bg-primary-hover text-white px-10 py-5 rounded-2xl font-black text-lg flex items-center gap-3 shadow-2xl shadow-primary/30 transition-all hover:-translate-y-1 active:scale-95"
              >
                Access the Suite
                <span className="material-symbols-outlined font-bold">arrow_forward</span>
              </button>
            </div>
          </div>
          <div className="relative animate-in fade-in zoom-in duration-1000 delay-200">
            <div className="absolute -inset-4 bg-gradient-to-tr from-primary/20 to-transparent blur-3xl opacity-50"></div>
            <div className="relative bg-slate-900 dark:bg-surface-dark border border-slate-800 rounded-[2.5rem] shadow-2xl overflow-hidden aspect-square flex items-center justify-center p-8">
              <div className="grid grid-cols-2 gap-4 w-full h-full opacity-40 group hover:opacity-100 transition-opacity duration-500">
                <div className="bg-slate-800 rounded-3xl p-6 flex flex-col justify-between transform hover:scale-105 transition-transform border border-slate-700">
                  <span className="material-symbols-outlined text-primary text-4xl">description</span>
                  <p className="text-xs font-bold text-slate-400">Summarization Engine</p>
                </div>
                <div className="bg-slate-800 rounded-3xl p-6 flex flex-col justify-between transform hover:scale-105 transition-transform border border-slate-700">
                  <span className="material-symbols-outlined text-green-500 text-4xl">verified_user</span>
                  <p className="text-xs font-bold text-slate-400">Forensic Verifier</p>
                </div>
                <div className="bg-slate-800 rounded-3xl p-6 flex flex-col justify-between transform hover:scale-105 transition-transform border border-slate-700">
                  <span className="material-symbols-outlined text-amber-500 text-4xl">edit_document</span>
                  <p className="text-xs font-bold text-slate-400">Agentic Drafting</p>
                </div>
                <div className="bg-slate-800 rounded-3xl p-6 flex flex-col justify-between transform hover:scale-105 transition-transform border border-slate-700">
                  <span className="material-symbols-outlined text-purple-500 text-4xl">search</span>
                  <p className="text-xs font-bold text-slate-400">Precedent Copilot</p>
                </div>
              </div>
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                 <div className="size-24 bg-primary rounded-full blur-2xl opacity-40 animate-pulse"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-32 bg-slate-50 dark:bg-card-dark/30 border-y border-slate-100 dark:border-border-dark px-8 md:px-16">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20 space-y-4">
            <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-primary">Capabilities</h2>
            <h3 className="text-4xl md:text-5xl font-black">Built for Critical Legal Analysis</h3>
            <p className="text-slate-500 max-w-2xl mx-auto">Four core modules designed to handle the complexity of modern caseloads with military-grade precision.</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-white dark:bg-surface-dark p-10 rounded-[2rem] border border-slate-200 dark:border-border-dark shadow-sm hover:shadow-xl transition-all hover:-translate-y-2 group">
              <div className="size-14 bg-blue-500/10 rounded-2xl flex items-center justify-center text-blue-500 mb-8 group-hover:bg-blue-500 group-hover:text-white transition-colors">
                <span className="material-symbols-outlined text-3xl">description</span>
              </div>
              <h4 className="text-xl font-bold mb-4">Intelligent Summarizer</h4>
              <p className="text-sm text-slate-500 leading-relaxed mb-6">Convert 100-page contracts into structured executive summaries. Automated risk identification and obligation mapping.</p>
              <ul className="text-[11px] font-bold text-slate-400 space-y-2 uppercase tracking-wide">
                <li className="flex items-center gap-2"><span className="size-1 bg-blue-500 rounded-full"></span> Multi-modal PDF Scan</li>
                <li className="flex items-center gap-2"><span className="size-1 bg-blue-500 rounded-full"></span> Risk Flagging</li>
              </ul>
            </div>

            <div className="bg-white dark:bg-surface-dark p-10 rounded-[2rem] border border-slate-200 dark:border-border-dark shadow-sm hover:shadow-xl transition-all hover:-translate-y-2 group">
              <div className="size-14 bg-green-500/10 rounded-2xl flex items-center justify-center text-green-500 mb-8 group-hover:bg-green-500 group-hover:text-white transition-colors">
                <span className="material-symbols-outlined text-3xl">verified_user</span>
              </div>
              <h4 className="text-xl font-bold mb-4">Forensic Verifier</h4>
              <p className="text-sm text-slate-500 leading-relaxed mb-6">Deep scan for document authenticity. Detects digital alterations, metadata red flags, and content inconsistencies.</p>
              <ul className="text-[11px] font-bold text-slate-400 space-y-2 uppercase tracking-wide">
                <li className="flex items-center gap-2"><span className="size-1 bg-green-500 rounded-full"></span> Alteration Detection</li>
                <li className="flex items-center gap-2"><span className="size-1 bg-green-500 rounded-full"></span> Integrity Scoring</li>
              </ul>
            </div>

            <div className="bg-white dark:bg-surface-dark p-10 rounded-[2rem] border border-slate-200 dark:border-border-dark shadow-sm hover:shadow-xl transition-all hover:-translate-y-2 group">
              <div className="size-14 bg-amber-500/10 rounded-2xl flex items-center justify-center text-amber-500 mb-8 group-hover:bg-amber-500 group-hover:text-white transition-colors">
                <span className="material-symbols-outlined text-3xl">edit_document</span>
              </div>
              <h4 className="text-xl font-bold mb-4">Agentic Drafting</h4>
              <p className="text-sm text-slate-500 leading-relaxed mb-6">A lawyer-agent-validator workflow. Convert raw requirements into bulletproof legal drafts automatically.</p>
              <ul className="text-[11px] font-bold text-slate-400 space-y-2 uppercase tracking-wide">
                <li className="flex items-center gap-2"><span className="size-1 bg-amber-500 rounded-full"></span> Multi-agent Pipeline</li>
                <li className="flex items-center gap-2"><span className="size-1 bg-amber-500 rounded-full"></span> Auto-Formatting</li>
              </ul>
            </div>

            <div className="bg-white dark:bg-surface-dark p-10 rounded-[2rem] border border-slate-200 dark:border-border-dark shadow-sm hover:shadow-xl transition-all hover:-translate-y-2 group">
              <div className="size-14 bg-purple-500/10 rounded-2xl flex items-center justify-center text-purple-500 mb-8 group-hover:bg-purple-500 group-hover:text-white transition-colors">
                <span className="material-symbols-outlined text-3xl">search</span>
              </div>
              <h4 className="text-xl font-bold mb-4">Precedent Discovery</h4>
              <p className="text-sm text-slate-500 leading-relaxed mb-6">Search global case law with Google Search grounding. Find matching citations and rulings for any factual scenario.</p>
              <ul className="text-[11px] font-bold text-slate-400 space-y-2 uppercase tracking-wide">
                <li className="flex items-center gap-2"><span className="size-1 bg-purple-500 rounded-full"></span> Search Grounding</li>
                <li className="flex items-center gap-2"><span className="size-1 bg-purple-500 rounded-full"></span> Citation Matching</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <footer className="py-12 border-t border-slate-100 dark:border-border-dark px-8 md:px-16 flex flex-col md:flex-row justify-between items-center gap-8">
        <div className="flex items-center gap-3">
          <div className="size-8 bg-slate-900 dark:bg-white rounded-lg flex items-center justify-center text-white dark:text-black">
            <span className="material-symbols-outlined font-bold text-lg">gavel</span>
          </div>
          <span className="text-lg font-black tracking-tighter">GAVEL</span>
        </div>
        <p className="text-slate-400 text-sm">© 2025 GAVEL Enterprise Legal Suite. All rights reserved.</p>
        <div className="flex gap-6">
          <a href="#" className="text-slate-400 hover:text-primary transition-colors text-sm">Privacy</a>
          <a href="#" className="text-slate-400 hover:text-primary transition-colors text-sm">Terms</a>
          <a href="#" className="text-slate-400 hover:text-primary transition-colors text-sm">Contact</a>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
