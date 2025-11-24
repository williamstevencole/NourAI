export interface Citation {
  id: string;
  label: string;
  organization: string;
  year: string;
  title: string;
  url?: string;
  excerpt?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
}

export interface QuickPrompt {
  id: string;
  text: string;
}

export interface ChatFilter {
  id: string;
  label: string;
  active: boolean;
}

export interface ClinicalData {
  age?: number;
  gender?: string;
  weight?: number;
  height?: number;
  conditions?: string[];
  allergies?: string[];
  medications?: string[];
  diet_type?: string;
  activity_level?: string;
}
