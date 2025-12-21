
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

export interface SummaryDashboard {
  case_name: string;
  neutral_citation: string;
  date_of_judgment: string;
  court_name: string;
  bench: string[];
  facts: string[];
  legal_issues: string[];
  statutes_cited: string[];
  precedents_cited: string[];
  ratio_decidendi: string;
  final_order: string;
  confidence_score: number;
  critique_feedback: string;
  raw_document_text: string;
}

export interface CopilotResponse {
  raw_facts: string;
  parties: Record<string, any>;
  chronology: any[];
  legal_issues: string[];
  precedents: Precedent[];
  legal_memo: string;
  interaction_history: any[];
}
