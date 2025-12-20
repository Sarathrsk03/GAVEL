
import React, { useState } from 'react';
import { Precedent } from '../types';
import { ENDPOINTS } from '../config';


interface CopilotResponse {
  raw_facts: string;
  parties: Record<string, any>;
  chronology: any[];
  legal_issues: string[];
  precedents: Precedent[];
  legal_memo: string;
  interaction_history: any[];
}

const PrecedentCopilot: React.FC = () => {
  const [inquiry, setInquiry] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<CopilotResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!inquiry.trim()) return;
    setLoading(true);
    setAnalysis(null);
    setError(null);

    try {
      const response = await fetch(ENDPOINTS.SEARCH, {

        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ facts: inquiry }),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data: CopilotResponse = await response.json();
      setAnalysis(data);
    } catch (err: any) {
      console.error(err);
      setError('Connection to analysis engine failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-background-light dark:bg-background-dark overflow-hidden">
      <header className="h-16 shrink-0 border-b border-slate-200 dark:border-border-dark bg-white dark:bg-surface-dark flex items-center justify-between px-8">
        <div className="flex items-center gap-3">
          <span className="material-symbols-outlined text-primary text-2xl">search</span>
          <h2 className="font-bold text-lg">Precedent Discovery</h2>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
        <div className="max-w-6xl mx-auto space-y-8">
          <div>
            <h1 className="text-3xl font-black mb-2 tracking-tight">Precedent Discovery</h1>
            <p className="text-slate-500 text-sm">Input case facts and let the AI Agent search across global legal databases for matching precedents.</p>
          </div>

          <div className="bg-white dark:bg-card-dark rounded-2xl border border-slate-200 dark:border-border-dark p-6 shadow-sm">
            <textarea
              value={inquiry}
              onChange={(e) => setInquiry(e.target.value)}
              className="w-full h-32 bg-slate-50 dark:bg-background-dark/50 border-slate-200 dark:border-border-dark rounded-xl p-4 text-sm focus:ring-primary mb-4 resize-none shadow-inner outline-none"
              placeholder="Describe the legal issue, scenario, or set of facts in detail..."
            />
            <button
              onClick={handleAnalyze}
              disabled={loading || !inquiry.trim()}
              className="w-full bg-primary hover:bg-primary-hover text-white py-4 rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg shadow-primary/20 disabled:opacity-50 transition-all active:scale-[0.98]"
            >
              <span className="material-symbols-outlined">{loading ? 'sync' : 'travel_explore'}</span>
              {loading ? 'Analyzing Facts & Searching Databases...' : 'Find Legal Precedents'}
            </button>
            {error && <p className="mt-4 text-xs text-red-500 font-bold text-center">{error}</p>}
          </div>

          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center text-center animate-in fade-in duration-300">
              <div className="size-16 rounded-full border-4 border-primary/20 border-t-primary animate-spin mb-6"></div>
              <h3 className="text-lg font-black mb-1">Agent is Working</h3>
              <p className="text-xs text-slate-400 uppercase tracking-widest font-bold animate-pulse">Scanning Precedents & Drafting Memo...</p>
            </div>
          ) : analysis && (
            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {/* Legal Memo */}
              <div className="bg-slate-900 text-white rounded-2xl p-8 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-5">
                  <span className="material-symbols-outlined text-9xl">description</span>
                </div>
                <div className="relative z-10 space-y-4">
                  <div className="flex items-center gap-2 text-primary">
                    <span className="material-symbols-outlined">contract</span>
                    <h3 className="text-[10px] font-black uppercase tracking-widest">Legal Analysis Memo</h3>
                  </div>
                  <div className="prose prose-invert prose-sm max-w-none whitespace-pre-wrap leading-relaxed opacity-90">
                    {analysis.legal_memo || "No memo generated."}
                  </div>
                </div>
              </div>

              {/* Precedents Section */}
              <div className="space-y-6">
                <div className="flex items-center justify-between border-b border-slate-200 dark:border-border-dark pb-2">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary">library_books</span>
                    <h3 className="font-black text-xl tracking-tight">Matching Precedents</h3>
                  </div>
                  <span className="text-[10px] bg-slate-100 dark:bg-slate-800 px-3 py-1 rounded-full font-bold text-slate-500 uppercase">
                    {Array.isArray(analysis.precedents) ? analysis.precedents.length : 0} Recovered
                  </span>
                </div>

                <div className="grid gap-6">
                  {Array.isArray(analysis.precedents) && analysis.precedents.length > 0 ? (
                    analysis.precedents.map((p, idx) => (
                      <div key={idx} className="bg-white dark:bg-card-dark rounded-2xl border border-slate-200 dark:border-border-dark p-6 shadow-sm hover:border-primary/30 transition-all group">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h4 className="text-lg font-black group-hover:text-primary transition-colors">{p.title || 'Untitled Precedent'}</h4>
                            <p className="text-xs font-bold text-slate-400 mt-1 uppercase tracking-tight">{p.citation || 'No Citation Provided'}</p>
                          </div>
                          <div className="flex items-center gap-1.5 px-3 py-1 bg-green-500/10 rounded-full border border-green-500/20">
                            <span className="text-[10px] font-black text-green-600 uppercase">
                              {p.matchScore || 0}% Match
                            </span>
                          </div>
                        </div>
                        <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed mb-4">{p.summary}</p>

                        {(p.tags || []).length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {p.tags?.map((tag, i) => (
                              <span key={i} className="text-[10px] bg-slate-50 dark:bg-slate-800 px-2 py-1 rounded-md text-slate-500 border border-slate-100 dark:border-slate-700 font-bold uppercase">
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-12 opacity-30">
                      <span className="material-symbols-outlined text-4xl mb-2">find_in_page</span>
                      <p className="text-sm font-bold">No direct precedents found for this inquiry</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PrecedentCopilot;
