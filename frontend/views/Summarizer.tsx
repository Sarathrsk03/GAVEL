
import React, { useState, useRef } from 'react';
import { ENDPOINTS } from '../config';
import { SummaryDashboard } from '../types';

interface SummarizerProps {
  summaryData: SummaryDashboard | null;
  setSummaryData: (data: SummaryDashboard | null) => void;
}

const Summarizer: React.FC<SummarizerProps> = ({ summaryData, setSummaryData }) => {
  const [inputText, setInputText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [base64Data, setBase64Data] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      processFile(selectedFile);
    }
  };

  const processFile = (selectedFile: File) => {
    setFile(selectedFile);
    const reader = new FileReader();
    reader.onload = (event) => {
      const result = event.target?.result as string;
      const base64 = result.split(',')[1];
      setBase64Data(base64);
      setInputText('');
    };
    reader.readAsDataURL(selectedFile);
  };

  const handleSummarize = async () => {
    if (!inputText.trim() && !base64Data) return;

    if (inputText.trim() && base64Data) {
      if (!window.confirm("Both text and file provided. The file will take precedence. Continue?")) {
        return;
      }
    }

    setLoading(true);

    setError(null);

    try {
      // Create FormData for multipart/form-data upload
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
      } else if (inputText) {
        // If there's only text, the backend currently expects a PDF file.
        // We'll create a blob if the user provided text but no file.
        const blob = new Blob([inputText], { type: 'text/plain' });
        formData.append('file', blob, 'input.txt');
      }

      const response = await fetch(ENDPOINTS.SUMMARIZE, {

        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `API error: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Backend Response Data:', data);
      // Backend returns { session_id, summary }
      if (data && data.summary) {
        setSummaryData(data.summary);
      } else {
        throw new Error('API response missing summary data');
      }
    } catch (err: any) {
      console.error('Summarization Error:', err);
      // Fallback for demonstration if endpoint is not reachable in this preview
      console.warn('Backend API call failed. Ensure your REST endpoint is configured.', err);
      setError('Backend connection error. Please ensure the summarization service is active.');

      // NOTE: Remove this block in production once the backend is linked
      /*
      setSummaryData({
        case_name: "Mock Judgment Result",
        neutral_citation: "[2025] GAVEL 01",
        date_of_judgment: "October 12, 2025",
        court_name: "Supreme Court of Justice",
        bench: ["Justice A. Sterling", "Justice B. Knight"],
        facts: ["The appellant filed for breach of contract.", "Defendant argued force majeure."],
        legal_issues: ["Whether digital signatures are valid under Section 4.", "Interpretation of Clause 12.1."],
        statutes_cited: ["Contract Act, 1872", "IT Act, 2000"],
        precedents_cited: ["Smith v. Jones (2010)", "Alpha Corp v. Beta (2018)"],
        ratio_decidendi: "Digital intent is manifest through multi-factor authentication.",
        final_order: "Appeal Dismissed.",
        confidence_score: 0.94,
        critique_feedback: "Analysis complete. Precedent citations verified against global database.",
        raw_document_text: ""
      });
      */
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setFile(null);
    setBase64Data(null);
    setInputText('');
    setSummaryData(null);
    setError(null);
  };

  return (
    <div className="h-full flex flex-col lg:flex-row overflow-hidden bg-background-light dark:bg-background-dark">
      {/* Input Panel (Left Side) */}
      <div className="w-full lg:w-[400px] border-r border-slate-200 dark:border-border-dark flex flex-col p-6 overflow-y-auto shrink-0 bg-white dark:bg-surface-dark/50">
        <h2 className="text-xl font-black mb-1">Legal Summarizer</h2>

        <div
          onClick={() => fileInputRef.current?.click()}
          className={`group border-2 border-dashed rounded-2xl p-6 flex flex-col items-center gap-3 transition-all cursor-pointer mb-6 ${file ? 'border-primary bg-primary/5' : 'border-slate-200 dark:border-border-dark hover:border-primary bg-slate-50 dark:bg-background-dark/30'
            }`}
        >
          <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept=".pdf,image/*" />
          <div className={`size-10 rounded-full flex items-center justify-center ${file ? 'bg-primary text-white' : 'bg-primary/10 text-primary'}`}>
            <span className="material-symbols-outlined">{file ? 'check' : 'upload_file'}</span>
          </div>
          <div className="text-center">
            {file ? (
              <p className="text-xs font-bold truncate max-w-[200px]">{file.name}</p>
            ) : (
              <p className="text-xs font-bold">Upload PDF / Image</p>
            )}
          </div>
        </div>

        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Or paste judgment text here..."
          className="w-full h-64 bg-slate-50 dark:bg-background-dark border border-slate-200 dark:border-border-dark rounded-xl p-4 text-sm focus:ring-primary mb-6 resize-none shadow-inner outline-none"
        />

        <button
          onClick={handleSummarize}
          disabled={loading || (!inputText && !base64Data)}
          className={`w-full flex items-center justify-center gap-2 bg-primary hover:bg-primary-hover text-white h-14 rounded-xl text-sm font-bold shadow-lg shadow-primary/20 transition-all active:scale-95 disabled:opacity-50`}
        >
          <span className="material-symbols-outlined">{loading ? 'sync' : 'send'}</span>
          {loading ? 'Processing via API...' : 'Generate Dashboard'}
        </button>

        {error && <p className="mt-4 text-[10px] text-red-500 font-bold text-center uppercase tracking-widest leading-relaxed">{error}</p>}
      </div>

      {/* Result Dashboard (Right Side) */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-6 lg:p-10 bg-slate-50 dark:bg-background-dark">
        {loading ? (
          <div className="h-full flex flex-col items-center justify-center text-center animate-in fade-in duration-300">
            <div className="relative mb-8">
              <div className="size-20 rounded-full border-4 border-primary/20 border-t-primary animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="material-symbols-outlined text-primary animate-pulse">sync</span>
              </div>
            </div>
            <h3 className="text-xl font-black mb-2 tracking-tight">AI Agent is Analyzing</h3>
            <p className="text-xs text-slate-500 uppercase tracking-widest font-bold animate-pulse">Extracting facts, issues & precedents...</p>
          </div>
        ) : summaryData ? (
          <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* ... existing header and grid content ... */}
            {/* Header / Case Name */}
            <div className="flex flex-col md:flex-row justify-between items-start mb-4 gap-4">
              <div className="flex-1">
                <h1 className="text-3xl font-black tracking-tight text-slate-900 dark:text-white leading-tight mb-2">
                  {summaryData?.case_name || 'Judgment Summary'}
                </h1>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1.5 px-3 py-1 bg-primary/10 rounded-full border border-primary/20">
                    <span className="material-symbols-outlined text-primary text-xs font-bold">verified</span>
                    <span className="text-[10px] font-black text-primary uppercase tracking-widest">
                      {Math.round((summaryData?.confidence_score || 0) * 100)}% Agent Confidence Score
                    </span>
                  </div>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                    External System Report
                  </span>
                </div>
              </div>
              <div className="flex gap-2">
                <button onClick={reset} className="size-10 rounded-full flex items-center justify-center bg-white dark:bg-surface-dark border border-slate-200 dark:border-border-dark text-slate-400 hover:text-red-500 transition-colors shadow-sm">
                  <span className="material-symbols-outlined">delete</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Judicial Metadata Box */}
              <div className="lg:col-span-8 bg-white dark:bg-surface-dark border border-slate-200 dark:border-border-dark rounded-2xl p-6 shadow-sm">
                <div className="flex items-center gap-2 mb-4 text-primary">
                  <span className="material-symbols-outlined">account_balance</span>
                  <h3 className="text-[10px] font-black uppercase tracking-widest">Judicial Metadata</h3>
                </div>
                <div className="grid md:grid-cols-3 gap-6">
                  <div>
                    <p className="text-[9px] font-bold text-slate-400 uppercase mb-1">Court Name</p>
                    <p className="text-sm font-bold">{summaryData?.court_name || 'Not specified'}</p>
                  </div>
                  <div>
                    <p className="text-[9px] font-bold text-slate-400 uppercase mb-1">Date of Judgement</p>
                    <p className="text-sm font-bold">{summaryData?.date_of_judgment || 'Not specified'}</p>
                  </div>
                  <div>
                    <p className="text-[9px] font-bold text-slate-400 uppercase mb-1">Neutral Citation</p>
                    <p className="text-sm font-bold">{summaryData?.neutral_citation || 'Not specified'}</p>
                  </div>
                </div>
              </div>

              {/* Bench Box */}
              <div className="lg:col-span-4 bg-white dark:bg-surface-dark border border-slate-200 dark:border-border-dark rounded-2xl p-6 shadow-sm">
                <div className="flex items-center gap-2 mb-4 text-amber-500">
                  <span className="material-symbols-outlined">groups</span>
                  <h3 className="text-[10px] font-black uppercase tracking-widest">The Bench</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {Array.isArray(summaryData?.bench) ? (
                    summaryData.bench.length > 0 ? summaryData.bench.map((judge, i) => (
                      <span key={i} className="px-3 py-1.5 bg-amber-500/5 text-amber-600 dark:text-amber-400 border border-amber-500/10 rounded-lg text-xs font-bold">
                        {judge}
                      </span>
                    )) : <p className="text-xs text-slate-400 italic">No bench members identified</p>
                  ) : typeof summaryData?.bench === 'string' && summaryData.bench ? (
                    <span className="px-3 py-1.5 bg-amber-500/5 text-amber-600 dark:text-amber-400 border border-amber-500/10 rounded-lg text-xs font-bold">
                      {summaryData.bench}
                    </span>
                  ) : (
                    <p className="text-xs text-slate-400 italic">No bench members identified</p>
                  )}
                </div>
              </div>

              {/* Facts Box */}
              <div className="lg:col-span-7 bg-white dark:bg-surface-dark border border-slate-200 dark:border-border-dark rounded-2xl p-8 shadow-sm">
                <div className="flex items-center gap-2 mb-6 text-blue-500">
                  <span className="material-symbols-outlined">info</span>
                  <h3 className="text-[10px] font-black uppercase tracking-widest">Facts of the Case</h3>
                </div>
                <ul className="space-y-4">
                  {Array.isArray(summaryData?.facts) ? (
                    summaryData.facts.length > 0 ? summaryData.facts.map((fact, i) => (
                      <li key={i} className="flex gap-3 text-sm leading-relaxed text-slate-600 dark:text-slate-300">
                        <span className="size-1.5 shrink-0 rounded-full bg-blue-500 mt-2"></span>
                        {fact}
                      </li>
                    )) : <p className="text-xs text-slate-400 italic">No facts extracted</p>
                  ) : typeof summaryData?.facts === 'string' && summaryData.facts ? (
                    <li className="text-sm leading-relaxed text-slate-600 dark:text-slate-300 whitespace-pre-wrap">
                      {summaryData.facts}
                    </li>
                  ) : (
                    <p className="text-xs text-slate-400 italic">No facts extracted</p>
                  )}
                </ul>
              </div>

              {/* Legal Issues Box */}
              <div className="lg:col-span-5 bg-white dark:bg-surface-dark border border-slate-200 dark:border-border-dark rounded-2xl p-8 shadow-sm">
                <div className="flex items-center gap-2 mb-6 text-purple-500">
                  <span className="material-symbols-outlined">gavel</span>
                  <h3 className="text-[10px] font-black uppercase tracking-widest">Legal Issues</h3>
                </div>
                <ul className="space-y-4">
                  {Array.isArray(summaryData?.legal_issues) ? (
                    summaryData.legal_issues.length > 0 ? summaryData.legal_issues.map((issue, i) => (
                      <li key={i} className="flex gap-3 text-sm font-medium leading-relaxed text-slate-700 dark:text-slate-200">
                        <span className="size-5 shrink-0 rounded bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-[10px] font-bold text-slate-400">{i + 1}</span>
                        {issue}
                      </li>
                    )) : <p className="text-xs text-slate-400 italic">No issues identified</p>
                  ) : typeof summaryData?.legal_issues === 'string' && summaryData.legal_issues ? (
                    <li className="text-sm font-medium leading-relaxed text-slate-700 dark:text-slate-200">
                      {summaryData.legal_issues}
                    </li>
                  ) : (
                    <p className="text-xs text-slate-400 italic">No issues identified</p>
                  )}
                </ul>
              </div>

              {/* Ratio & Final Order Box */}
              <div className="lg:col-span-12 bg-slate-900 text-white rounded-2xl p-8 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-5">
                  <span className="material-symbols-outlined text-9xl">check_circle</span>
                </div>
                <div className="relative z-10 grid md:grid-cols-2 gap-12">
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 text-primary">
                      <span className="material-symbols-outlined">psychology</span>
                      <h3 className="text-[10px] font-black uppercase tracking-widest text-primary">Ratio Decidendi</h3>
                    </div>
                    <p className="text-sm font-medium leading-relaxed italic opacity-90">
                      "{summaryData?.ratio_decidendi || 'Decision rationale not provided'}"
                    </p>
                  </div>
                  <div className="space-y-6">
                    <div>
                      <div className="flex items-center gap-2 mb-4 text-green-400">
                        <span className="material-symbols-outlined">task_alt</span>
                        <h3 className="text-[10px] font-black uppercase tracking-widest text-green-400">Final Order</h3>
                      </div>
                      <p className="text-sm font-bold leading-relaxed">
                        {summaryData?.final_order || 'Order not provided'}
                      </p>
                    </div>
                    <div className="pt-6 border-t border-white/10">
                      <div className="flex items-center gap-2 mb-2 text-slate-400">
                        <span className="material-symbols-outlined text-sm">comment</span>
                        <h3 className="text-[9px] font-black uppercase tracking-widest">Critique & Feedback</h3>
                      </div>
                      <p className="text-[11px] text-slate-400 leading-relaxed italic">
                        {summaryData?.critique_feedback || 'No automated critique available'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Citations & Statutes Box */}
              <div className="lg:col-span-12 bg-white dark:bg-surface-dark border border-slate-200 dark:border-border-dark rounded-2xl p-8 shadow-sm">
                <div className="flex items-center gap-2 mb-6 text-green-500">
                  <span className="material-symbols-outlined">menu_book</span>
                  <h3 className="text-[10px] font-black uppercase tracking-widest">Citations & Authorities</h3>
                </div>
                <div className="grid md:grid-cols-2 gap-8">
                  <div>
                    <h4 className="text-[9px] font-bold text-slate-400 uppercase mb-3 tracking-widest">Statutes Cited</h4>
                    <div className="flex flex-wrap gap-2">
                      {Array.isArray(summaryData?.statutes_cited) ? (
                        summaryData.statutes_cited.length > 0 ? summaryData.statutes_cited.map((s, i) => (
                          <span key={i} className="px-3 py-1.5 bg-green-500/5 text-green-600 border border-green-500/10 rounded-lg text-xs font-bold">{s}</span>
                        )) : <p className="text-xs text-slate-400 italic">None</p>
                      ) : typeof summaryData?.statutes_cited === 'string' && summaryData.statutes_cited ? (
                        <span className="px-3 py-1.5 bg-green-500/5 text-green-600 border border-green-500/10 rounded-lg text-xs font-bold">{summaryData.statutes_cited}</span>
                      ) : (
                        <p className="text-xs text-slate-400 italic">None</p>
                      )}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-[9px] font-bold text-slate-400 uppercase mb-3 tracking-widest">Precedents Cited</h4>
                    <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {Array.isArray(summaryData?.precedents_cited) ? (
                        summaryData.precedents_cited.length > 0 ? summaryData.precedents_cited.map((p, i) => (
                          <li key={i} className="text-xs font-medium flex gap-2 text-slate-600 dark:text-slate-400">
                            <span className="material-symbols-outlined text-sm">link</span>
                            {p}
                          </li>
                        )) : <p className="text-xs text-slate-400 italic">None</p>
                      ) : typeof summaryData?.precedents_cited === 'string' && summaryData.precedents_cited ? (
                        <li className="text-xs font-medium flex gap-2 text-slate-600 dark:text-slate-400">
                          <span className="material-symbols-outlined text-sm">link</span>
                          {summaryData.precedents_cited}
                        </li>
                      ) : (
                        <p className="text-xs text-slate-400 italic">None</p>
                      )}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="h-full min-h-[500px] flex flex-col items-center justify-center text-center opacity-40">
            <div className="size-24 bg-slate-200 dark:bg-slate-800 rounded-full flex items-center justify-center mb-6">
              <span className="material-symbols-outlined text-5xl">dashboard</span>
            </div>
            <h3 className="text-2xl font-black mb-2">Judgment Dashboard</h3>
            <p className="text-sm max-w-[320px] mx-auto leading-relaxed">
              Input a document and trigger the API to populate an interactive analysis dashboard.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Summarizer;
