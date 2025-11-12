// types/paper.ts - COMPLETE VERSION WITH SIMPLIFIED AI SETTINGS

// ==================== PAPER SECTION ====================

export interface PaperSection {
  id: string;
  title: string;
  content: string;
  status: 'not-started' | 'in-progress' | 'completed' | 'needs-review';
  lastModified: Date;
  wordCount: number;
  order: number;
}

// ==================== AI SETTINGS (SIMPLIFIED - NO GLOBAL) ====================

export interface PaperAISettings {
  labLevel: number;
  personalLevel: number;
  globalLevel: number;
  writingStyle: 'academic' | 'concise' | 'detailed' | 'collaborative';
  contextDepth: 'minimal' | 'moderate' | 'comprehensive';
  researchFocus: string[];
  suggestionsEnabled: boolean;
}

export interface PaperAISettingsResponse {
  paperId: string;
  settings: PaperAISettings;
}

// ==================== PAPER ====================

export interface Paper {
  id: string;
  title: string;
  abstract: string;
  status: 'draft' | 'in-progress' | 'in-review' | 'revision' | 'completed' | 'published' | 'archived';
  createdAt: Date;
  lastModified: Date;
  progress: number;
  targetWordCount: number;
  currentWordCount: number;
  coAuthors: string[];
  researchArea: string;
  sections: PaperSection[];
  tags: string[];
  isPublic: boolean;
  doi?: string;
  journal?: string;
  publicationDate?: Date;
  citationCount?: number;
  
  // ✅ AI Settings (per-paper only)
  aiSettings?: PaperAISettings;
}

// ==================== RESEARCH WORKFLOW ====================

export interface ResearchPhase {
  id: string;
  name: string;
  status: 'completed' | 'in-progress' | 'pending' | 'overdue';
  progress: number;
  startDate: Date;
  dueDate: Date;
  estimatedHours: number;
  actualHours: number;
  tasks: Task[];
  paperId: string;
}

export interface Task {
  id: string;
  name: string;
  description?: string;
  status: 'completed' | 'in-progress' | 'pending';
  priority: 'high' | 'medium' | 'low';
  dueDate: Date;
  assignee?: string;
  notes?: string;
  phaseId: string;
  paperId: string;
}

export interface Milestone {
  id: string;
  title: string;
  description: string;
  date: Date;
  status: 'completed' | 'upcoming' | 'overdue';
  paperId: string;
}

// ==================== REFERENCES ====================

export interface Reference {
  id: string;
  title: string;
  authors: string[];
  journal: string;
  year: number;
  doi?: string;
  url?: string;
  notes?: string;
  tags: string[];
  paperId: string;
}

// ==================== COLLABORATION ====================

export interface CollaborationInvite {
  id: string;
  paperId: string;
  invitedEmail: string;
  invitedBy: string;
  role: 'viewer' | 'editor' | 'co-author';
  status: 'pending' | 'accepted' | 'declined';
  createdAt: Date;
  expiresAt: Date;
}

export interface PaperVersion {
  id: string;
  paperId: string;
  version: string;
  title: string;
  abstract: string;
  content: string;
  createdAt: Date;
  createdBy: string;
  changes: string;
}

export interface PaperComment {
  id: string;
  paperId: string;
  sectionId?: string;
  content: string;
  authorId: string;
  authorName: string;
  createdAt: Date;
  resolved: boolean;
  parentId?: string;
  replies?: PaperComment[];
}

// ==================== TYPE ALIASES ====================

export type PaperStatus = Paper['status'];
export type SectionStatus = PaperSection['status'];  
export type TaskStatus = Task['status'];
export type TaskPriority = Task['priority'];