import React, { useState, useEffect } from 'react';
import { ENDPOINTS } from '../config';
import { SummaryDashboard } from '../types';


type WorkflowStage = 'REQUIREMENTS' | 'DRAFTING' | 'REVISION';

interface RevisionSuggestion {
  id: string;
  originalText: string;
  suggestedText: string;
  precedentSource: string;
  reasoning: string;
}

interface DraftHelperProps {
  summaryData: SummaryDashboard | null;
  requirements: string;
  docType: string;
  jurisdiction: string;
  setState: (state: { requirements: string; docType: string; jurisdiction: string; }) => void;
}

const DraftHelper: React.FC<DraftHelperProps> = ({ summaryData, requirements, docType, jurisdiction, setState }) => {
  const [stage, setStage] = useState<WorkflowStage>('REQUIREMENTS');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const summaryLoadedRef = React.useRef(false);

  useEffect(() => {
    // Only populate from summaryData if:
    // 1. summaryData exists
    // 2. We haven't already loaded it (to prevent overwriting user edits)
    // 3. Requirements are currently empty (user hasn't typed anything)
    if (summaryData && !summaryLoadedRef.current && !requirements) {
      const {
        case_name, facts, legal_issues, ratio_decidendi, final_order
      } = summaryData;

      const summaryText = `
        Case Name: ${case_name}
        Facts: ${facts.join(', ')}
        Legal Issues: ${legal_issues.join(', ')}
        Ratio Decidendi: ${ratio_decidendi}
        Final Order: ${final_order}
      `.trim();

      setState({ requirements: summaryText, docType, jurisdiction });
      summaryLoadedRef.current = true;
    }
  }, [summaryData, requirements, docType, jurisdiction, setState]);
  const [statusMsg, setStatusMsg] = useState('');
  const [revisions, setRevisions] = useState<RevisionSuggestion[]>([]);
  const [generatedFile, setGeneratedFile] = useState<{ url: string; name: string } | null>(null);

  const startDrafting = async () => {
    if (!requirements.trim()) return;
    setLoading(true);
    setStage('DRAFTING');
    setStatusMsg('Drafting Agent is converting requirements into legal form...');
    setGeneratedFile(null);
    setContent('');

    try {
      // Use the DRAFT endpoint which runs the full workflow (Drafting + Validation)
      const response = await fetch(ENDPOINTS.DRAFT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          requirements: `Type: ${docType}. Jurisdiction: ${jurisdiction}. Requirements: ${requirements}`,
          user_context: "User initiated draft via GAVEL frontend."
        })
      });

      if (!response.ok) throw new Error(`Drafting API error: ${response.statusText}`);

      const data = await response.json();

      if (data.status === "completed" && data.download_url) {
        setStatusMsg("Draft generated and validated successfully.");

        // Use the static file URL directly
        setGeneratedFile({
          url: data.download_url,
          name: data.file_name || 'Legal_Draft.docx'
        });

        setContent("Draft generated successfully. Please download the document to view the final validated legal agreement.");
        setStage('REVISION');
      } else {
        setContent(`Drafting process completed, but no document was returned. Message: ${data.message}`);
      }

    } catch (err) {
      console.error(err);
      setStatusMsg('Error during drafting.');
      setContent(`Error: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  // Deprecated: Backend runs validation automatically in the loop.
  const runValidation = async (currentDraft: string) => {
    // Placeholder to keep code structure if needed for future interactive mode
    console.log("Validation is handled by the backend workflow automatically.");
  };

  const applyRevision = (rev: RevisionSuggestion) => {
    setContent(prev => prev.split(rev.originalText).join(rev.suggestedText));
    setRevisions(prev => prev.filter(r => r.id !== rev.id));
  };

  return (
    <div className="h-full flex overflow-hidden bg-background-light dark:bg-background-dark">
      {/* Configuration Sidebar */}
      <aside className="w-72 border-r border-slate-200 dark:border-border-dark bg-white dark:bg-surface-dark flex flex-col shrink-0">
        <div className="p-6 border-b border-slate-200 dark:border-border-dark">
          <h2 className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-6 flex items-center gap-2">
            <span className="material-symbols-outlined text-sm">settings_applications</span>
            Workflow Settings
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1.5">Document Form</label>
              <select
                value={docType}
                onChange={(e) => setState({ requirements, docType: e.target.value, jurisdiction })}
                className="w-full bg-slate-50 dark:bg-background-dark border-slate-200 dark:border-border-dark rounded-lg text-xs font-bold p-2 focus:ring-primary"
              >
                <option>Service Agreement</option>
                <option>Motion to Dismiss</option>
                <option>Non-Disclosure Agreement</option>
                <option>Employment Contract</option>
              </select>
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1.5">Jurisdiction</label>
              <input
                value={jurisdiction}
                onChange={(e) => setState({ requirements, docType, jurisdiction: e.target.value })}
                className="w-full bg-slate-50 dark:bg-background-dark border-slate-200 dark:border-border-dark rounded-lg text-xs font-bold p-2 focus:ring-primary"
              />
            </div>
          </div>
        </div>

        <div className="flex-1 p-6">
          <div className="space-y-8">
            <div className={`flex gap-4 items-start ${stage === 'REQUIREMENTS' ? 'text-primary' : 'text-slate-400'}`}>
              <span className={`size-6 rounded-full flex items-center justify-center text-[10px] font-bold border-2 ${stage === 'REQUIREMENTS' ? 'border-primary bg-primary/10' : 'border-slate-300 dark:border-slate-700'}`}>1</span>
              <div>
                <p className="text-xs font-bold">Requirements</p>
                <p className="text-[10px] opacity-60">Define legal objectives</p>
              </div>
            </div>
            <div className={`flex gap-4 items-start ${stage === 'DRAFTING' ? 'text-primary' : 'text-slate-400'}`}>
              <span className={`size-6 rounded-full flex items-center justify-center text-[10px] font-bold border-2 ${stage === 'DRAFTING' ? 'border-primary bg-primary/10' : 'border-slate-300 dark:border-slate-700'}`}>2</span>
              <div>
                <p className="text-xs font-bold">AI Drafting</p>
                <p className="text-[10px] opacity-60">Agent generating draft</p>
              </div>
            </div>
            <div className={`flex gap-4 items-start ${stage === 'REVISION' ? 'text-primary' : 'text-slate-400'}`}>
              <span className={`size-6 rounded-full flex items-center justify-center text-[10px] font-bold border-2 ${stage === 'REVISION' ? 'border-primary bg-primary/10' : 'border-slate-300 dark:border-slate-700'}`}>3</span>
              <div>
                <p className="text-xs font-bold">Precedent Audit</p>
                <p className="text-[10px] opacity-60">Validator review</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Workspace */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        {loading && (
          <div className="absolute inset-0 bg-white/80 dark:bg-background-dark/80 backdrop-blur-sm z-50 flex flex-col items-center justify-center text-center p-12">
            <div className="size-16 relative mb-6">
              <div className="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-primary rounded-full border-t-transparent animate-spin"></div>
            </div>
            <p className="text-lg font-black tracking-tight">{statusMsg}</p>
            <p className="text-sm text-slate-500 mt-2">Connecting to legal agents and search engines...</p>
          </div>
        )}

        {stage === 'REQUIREMENTS' ? (
          <div className="flex-1 flex flex-col p-12 max-w-4xl mx-auto w-full">
            <h1 className="text-3xl font-black mb-2">Lawyer's Instruction Canvas</h1>
            <p className="text-slate-500 mb-8">Detail the key parties, terms, and specific objectives. The Drafting Agent will use this to build the initial document.</p>

            <div className="flex-1 bg-white dark:bg-card-dark border border-slate-200 dark:border-border-dark rounded-2xl shadow-xl p-8 flex flex-col">
              <label className="text-[10px] font-black uppercase text-primary tracking-widest mb-4">Core Requirements & Facts</label>
              <textarea
                value={requirements}
                onChange={(e) => setState({ requirements: e.target.value, docType, jurisdiction })}
                placeholder="E.g. Party A (Alpha Corp) hires Party B (Freelance Dev) for $50k backend work. Deliverables due in 3 months. Alpha Corp owns all IP. Dev gets 20% upfront."
                className="flex-1 bg-transparent border-none focus:ring-0 text-lg leading-relaxed resize-none p-0 outline-none"
              />
              <div className="mt-8 pt-8 border-t border-slate-100 dark:border-border-dark flex justify-between items-center">
                <div className="flex gap-4">
                  <button className="flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-slate-600">
                    <span className="material-symbols-outlined text-lg">attach_file</span> Attach Form
                  </button>
                  <button className="flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-slate-600">
                    <span className="material-symbols-outlined text-lg">mic</span> Voice Input
                  </button>
                </div>
                <button
                  onClick={startDrafting}
                  disabled={!requirements.trim()}
                  className="bg-primary hover:bg-primary-hover text-white px-8 py-3 rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-primary/20 transition-all active:scale-95 disabled:opacity-50"
                >
                  <span className="material-symbols-outlined">auto_awesome</span>
                  Generate First Draft
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col">
            <header className="h-14 bg-white dark:bg-surface-dark border-b border-slate-200 dark:border-border-dark flex items-center justify-between px-8">
              <div className="flex items-center gap-4">
                <span className="bg-primary/10 text-primary text-[10px] font-bold px-2 py-1 rounded">DRAFT v1.0</span>
                <h3 className="text-sm font-bold">{docType} - {jurisdiction}</h3>
              </div>
              <div className="flex gap-2">
                <button onClick={() => setStage('REQUIREMENTS')} className="text-xs font-bold text-slate-500 hover:text-primary px-3 py-1.5 transition-colors">Edit Requirements</button>

                {generatedFile && (
                  <a href={generatedFile.url} download={generatedFile.name} className="bg-primary text-white px-4 py-1.5 rounded-lg text-xs font-bold flex items-center gap-2">
                    <span className="material-symbols-outlined text-sm">download</span> Download DOCX
                  </a>
                )}
              </div>
            </header>

            <div className="flex-1 flex overflow-hidden">
              <div className="flex-1 overflow-y-auto p-12 bg-slate-100 dark:bg-background-dark custom-scrollbar">
                <div className="max-w-[800px] mx-auto bg-white dark:bg-card-dark min-h-[1000px] shadow-2xl rounded p-16 border border-slate-200 dark:border-border-dark/30">
                  <div className="prose dark:prose-invert">
                    <p className="whitespace-pre-wrap">{content}</p>
                  </div>
                </div>
              </div>

              {/* Validator Panel */}
              {stage === 'REVISION' && (
                <aside className="w-[380px] border-l border-slate-200 dark:border-border-dark bg-white dark:bg-surface-dark flex flex-col shrink-0">
                  <div className="p-6 border-b border-slate-200 dark:border-border-dark flex items-center justify-between bg-slate-50/50 dark:bg-background-dark/50">
                    <div className="flex items-center gap-2">
                      <span className="material-symbols-outlined text-primary">verified_user</span>
                      <h3 className="font-bold text-sm">AI Validator Audit</h3>
                    </div>
                    <span className="text-[10px] font-bold bg-green-500/10 text-green-500 px-2 py-0.5 rounded uppercase">Completed</span>
                  </div>

                  <div className="flex-1 p-6 flex flex-col justify-center items-center text-center opacity-60">
                    <span className="material-symbols-outlined text-6xl mb-4 text-green-500">check_circle</span>
                    <h3 className="text-lg font-bold mb-2">Draft validated!</h3>
                    <p className="text-sm">The document has been drafted by the agent and verified against precedents. You can download the final Word document now.</p>
                  </div>
                </aside>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default DraftHelper;
