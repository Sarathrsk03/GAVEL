
import React, { useState, useRef } from 'react';
import { Anomaly } from '../types';
import { ENDPOINTS } from '../config';

interface VerifierProps {
  file: File | null;
  results: { score: number; anomalies: Anomaly[] } | null;
  setState: (state: { file: File | null; results: { score: number; anomalies: Anomaly[] } | null }) => void;
}

const Verifier: React.FC<VerifierProps> = ({ file, results, setState }) => {
  const [base64Data, setBase64Data] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      processFile(selectedFile);
    }
  };

  const processFile = (selectedFile: File) => {
    setState({ file: selectedFile, results: null });
    const reader = new FileReader();
    reader.onload = (event) => {
      const result = event.target?.result as string;
      const base64 = result.split(',')[1];
      setBase64Data(base64);
    };
    reader.readAsDataURL(selectedFile);
  };

  const handleVerify = async () => {
    if (!base64Data || !file) return;
    setLoading(true);
    try {
      const response = await fetch(ENDPOINTS.VERIFY, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_name: file.name,
          mime_type: file.type || 'application/pdf',
          base64_data: base64Data,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `Server error: ${response.statusText}`);
      }

      const data = await response.json();
      setState({
        file,
        results: {
          score: data.authenticityScore ?? 0,
          anomalies: data.anomalies ?? []
        }
      });

    } catch (err) {
      console.error('Verification error:', err);
      alert('An error occurred during verification. Please ensure the file is a valid PDF or Image.');
    } finally {
      setLoading(false);
    }
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      processFile(droppedFile);
    }
  };

  return (
    <div className="h-full flex flex-col p-6 lg:p-12 overflow-y-auto bg-background-light dark:bg-background-dark custom-scrollbar">
      <div className="max-w-6xl mx-auto w-full">
        <div className="mb-12">
          <h1 className="text-4xl font-black mb-2 tracking-tight">Contract Authenticity Verifier</h1>
          <p className="text-slate-500 dark:text-text-secondary text-lg max-w-2xl">
            Upload a document for deep forensic analysis. We detect alterations, inconsistencies, and metadata red flags using multi-modal AI.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-7 space-y-6">
            <div className="bg-white dark:bg-card-dark rounded-2xl border border-slate-200 dark:border-border-dark shadow-sm p-8">
              <h3 className="font-bold mb-6 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">upload_file</span>
                Document Forensic Input
              </h3>

              <div
                onDragOver={onDragOver}
                onDrop={onDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`group border-2 border-dashed rounded-2xl py-20 flex flex-col items-center justify-center gap-4 transition-all cursor-pointer relative ${file ? 'border-primary bg-primary/5' : 'border-slate-200 dark:border-border-dark bg-slate-50 dark:bg-background-dark/50 hover:border-primary/50'
                  }`}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  className="hidden"
                  accept=".pdf,image/*"
                />

                <div className={`size-16 rounded-full flex items-center justify-center transition-transform group-hover:scale-110 ${file ? 'bg-primary text-white' : 'bg-primary/10 text-primary'
                  }`}>
                  <span className="material-symbols-outlined text-3xl font-bold">
                    {file ? 'check_circle' : 'cloud_upload'}
                  </span>
                </div>

                <div className="text-center px-4">
                  {file ? (
                    <>
                      <h3 className="text-lg font-bold mb-1 truncate max-w-xs mx-auto">{file.name}</h3>
                      <p className="text-xs text-slate-500 dark:text-text-secondary">Ready for forensic analysis ({(file.size / 1024 / 1024).toFixed(2)} MB)</p>
                    </>
                  ) : (
                    <>
                      <h3 className="text-lg font-bold mb-1">Upload Document</h3>
                      <p className="text-sm text-slate-500 dark:text-text-secondary">Drag and drop PDF or Image here, or click to browse</p>
                      <p className="text-[10px] text-slate-400 mt-2 uppercase font-bold tracking-widest">Supports PDF, PNG, JPG</p>
                    </>
                  )}
                </div>
              </div>

              <div className="mt-8 space-y-4">
                <div className="flex items-center gap-3 p-4 bg-slate-50 dark:bg-background-dark/30 rounded-xl border border-slate-100 dark:border-border-dark">
                  <span className="material-symbols-outlined text-slate-400">shield</span>
                  <div className="text-xs text-slate-500">
                    <p className="font-bold text-slate-700 dark:text-slate-300">Privacy Guaranteed</p>
                    <p>Documents are processed securely and never stored on our servers.</p>
                  </div>
                </div>
              </div>

              <button
                onClick={handleVerify}
                disabled={loading || !file}
                className="w-full mt-8 bg-primary hover:bg-primary-hover text-white h-14 rounded-2xl font-bold flex items-center justify-center gap-3 shadow-lg transition-all active:scale-95 disabled:opacity-50 disabled:grayscale"
              >
                <span className="material-symbols-outlined animate-spin-slow">{loading ? 'sync' : 'verified_user'}</span>
                {loading ? 'Performing Multi-modal Scan...' : 'Run Forensic Verification'}
              </button>
            </div>
          </div>

          <div className="lg:col-span-5 flex flex-col gap-6 min-h-[500px]">
            {results ? (
              <div className="flex-1 bg-white dark:bg-card-dark rounded-2xl border border-slate-200 dark:border-border-dark shadow-sm flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="p-10 flex flex-col items-center text-center border-b border-slate-100 dark:border-border-dark bg-gradient-to-b from-primary/5 to-transparent">
                  <div className="relative size-44 mb-6">
                    <svg className="size-full -rotate-90" viewBox="0 0 36 36">
                      <circle cx="18" cy="18" r="16" fill="none" className="stroke-slate-100 dark:stroke-slate-800" strokeWidth="3" />
                      <circle
                        cx="18" cy="18" r="16" fill="none"
                        className={`transition-all duration-1000 ${results.score > 70 ? 'stroke-green-500' : results.score > 40 ? 'stroke-amber-500' : 'stroke-red-500'}`}
                        strokeWidth="3"
                        strokeDasharray={`${results.score}, 100`}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-4xl font-black">{results.score}%</span>
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Auth Score</span>
                    </div>
                  </div>
                  <h3 className="text-lg font-bold mb-1">Verification Complete</h3>
                  <p className="text-sm text-slate-500 font-medium">
                    Scanned {file?.name}. Found {results.anomalies.length} anomalies.
                  </p>
                </div>

                <div className="p-8 flex-1 overflow-y-auto custom-scrollbar">
                  <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-6">Forensic Findings</h4>
                  <div className="space-y-4">
                    {results.anomalies.map((a) => (
                      <div key={a.id} className={`flex gap-4 p-4 rounded-xl border transition-all hover:translate-x-1 ${a.severity === 'high'
                          ? 'bg-red-500/5 border-red-500/20 text-red-700 dark:text-red-400'
                          : a.severity === 'medium'
                            ? 'bg-amber-500/5 border-amber-500/20 text-amber-700 dark:text-amber-400'
                            : 'bg-blue-500/5 border-blue-500/20 text-blue-700 dark:text-blue-400'
                        }`}>
                        <span className="material-symbols-outlined mt-1">
                          {a.severity === 'high' ? 'report' : a.severity === 'medium' ? 'warning' : 'info'}
                        </span>
                        <div>
                          <p className="text-sm font-bold">{a.title}</p>
                          <p className="text-xs opacity-80 mt-1 leading-relaxed">{a.description}</p>
                        </div>
                      </div>
                    ))}
                    {results.anomalies.length === 0 && (
                      <div className="text-center py-10 text-slate-400">
                        <span className="material-symbols-outlined text-4xl mb-2 text-green-500">verified</span>
                        <p className="text-sm">High Integrity Document.</p>
                        <p className="text-[10px]">No visible forensic anomalies were detected.</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="p-4 bg-slate-50 dark:bg-background-dark/50 border-t border-slate-200 dark:border-border-dark">
                  <button className="w-full py-2.5 text-[10px] font-black uppercase tracking-widest text-slate-500 hover:text-primary transition-colors">
                    Export Forensic Report (PDF)
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center bg-slate-50/50 dark:bg-card-dark/30 rounded-2xl border border-dashed border-slate-200 dark:border-border-dark text-slate-400 p-12 text-center">
                <div className="size-20 bg-slate-200 dark:bg-slate-800 rounded-full flex items-center justify-center mb-6 opacity-50">
                  <span className="material-symbols-outlined text-4xl">radar</span>
                </div>
                <h3 className="text-lg font-bold text-slate-500 dark:text-slate-400 mb-2">Awaiting Forensic Scan</h3>
                <p className="text-sm max-w-[240px] mx-auto leading-relaxed">
                  Once you upload a document and click verify, our AI will inspect the file structure and content for inconsistencies.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Verifier;
