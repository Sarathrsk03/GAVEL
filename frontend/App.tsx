
import React, { useState } from 'react';
import { AppView } from './types';
import LandingPage from './views/LandingPage';
import Summarizer from './views/Summarizer';
import Verifier from './views/Verifier';
import DraftHelper from './views/DraftHelper';
import PrecedentCopilot from './views/PrecedentCopilot';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<AppView>(AppView.LANDING);

  const renderView = () => {
    switch (currentView) {
      case AppView.LANDING: return <LandingPage onStart={() => setCurrentView(AppView.SUMMARIZER)} />;
      case AppView.SUMMARIZER: return <Summarizer />;
      case AppView.VERIFIER: return <Verifier />;
      case AppView.DRAFT_HELPER: return <DraftHelper />;
      case AppView.PRECEDENT_COPILOT: return <PrecedentCopilot />;
      default: return <LandingPage onStart={() => setCurrentView(AppView.SUMMARIZER)} />;
    }
  };

  const navItems = [
    { id: AppView.SUMMARIZER, label: 'Summarizer', icon: 'description' },
    { id: AppView.VERIFIER, label: 'Verifier', icon: 'verified_user' },
    { id: AppView.DRAFT_HELPER, label: 'Drafting', icon: 'edit_document' },
    { id: AppView.PRECEDENT_COPILOT, label: 'Precedents', icon: 'search' },
  ];

  const isLanding = currentView === AppView.LANDING;

  return (
    <div className="flex h-screen overflow-hidden bg-background-light dark:bg-background-dark">
      {/* Universal Sidebar - Hidden on Landing */}
      {!isLanding && (
        <aside className="w-20 lg:w-64 flex flex-col border-r border-slate-200 dark:border-border-dark bg-white dark:bg-surface-dark shrink-0 transition-all animate-in slide-in-from-left duration-300">
          <div className="p-4 flex items-center gap-3 border-b border-slate-200 dark:border-border-dark cursor-pointer" onClick={() => setCurrentView(AppView.LANDING)}>
            <div className="size-10 bg-primary/20 rounded-lg flex items-center justify-center text-primary shrink-0">
              <span className="material-symbols-outlined font-bold text-2xl">gavel</span>
            </div>
            <div className="hidden lg:block overflow-hidden">
              <h1 className="text-sm font-bold truncate">GAVEL</h1>
              <p className="text-[10px] text-slate-500 uppercase tracking-widest">Enterprise Suite</p>
            </div>
          </div>

          <nav className="flex-1 p-2 space-y-1 mt-4">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm font-medium ${
                  currentView === item.id
                    ? 'bg-primary text-white'
                    : 'text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 dark:text-slate-400'
                }`}
              >
                <span className="material-symbols-outlined text-xl">{item.icon}</span>
                <span className="hidden lg:inline">{item.label}</span>
              </button>
            ))}
          </nav>

          <div className="p-4 border-t border-slate-200 dark:border-border-dark space-y-4">
            <button className="flex items-center gap-3 w-full text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">
              <span className="material-symbols-outlined">settings</span>
              <span className="hidden lg:inline text-sm">Settings</span>
            </button>
            <div className="flex items-center gap-3">
               <div className="size-9 rounded-full bg-cover bg-center border border-slate-200 dark:border-border-dark" style={{backgroundImage: `url('https://picsum.photos/seed/legal/200')`}}></div>
               <div className="hidden lg:block overflow-hidden">
                 <p className="text-xs font-bold truncate">Sarah Jenkins</p>
                 <p className="text-[10px] text-slate-500">Senior Associate</p>
               </div>
            </div>
          </div>
        </aside>
      )}

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden relative">
        {renderView()}
      </main>
    </div>
  );
};

export default App;
