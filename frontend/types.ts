
export enum AppView {
  LANDING = 'landing',
  SUMMARIZER = 'summarizer',
  VERIFIER = 'verifier',
  DRAFT_HELPER = 'draft_helper',
  PRECEDENT_COPILOT = 'precedent_copilot',
}

export interface LegalDocument {
  id: string;
  name: string;
  size: string;
  status: 'ready' | 'summarized' | 'analyzing' | 'error';
  type: string;
}

export interface Anomaly {
  id: string;
  title: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
}

export interface Fact {
  id: string;
  text: string;
  relevance: 'high' | 'medium' | 'context';
  source: string;
}

export interface Precedent {
  id: string;
  title: string;
  citation: string;
  matchScore: number;
  summary: string;
  tags: string[];
  date: string;
  court: string;
}
