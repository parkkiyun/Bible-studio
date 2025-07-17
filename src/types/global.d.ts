import { ElectronAPI } from '../preload';

declare global {
  interface Window {
    electronAPI: {
      getBibleBooks: () => Promise<any[]>;
      getBibleVerses: (book: string, chapter: number, version: string) => Promise<any[]>;
      getCommentaries: (book: string, chapter: number) => Promise<any[]>;
      searchVerses: (query: string, version: string) => Promise<any[]>;
      // 개발자 API
      getVersions: () => Promise<any[]>;
      addVersion: (versionData: any) => Promise<boolean>;
      deleteVersion: (versionId: string) => Promise<boolean>;
      updateVersionName: (versionId: string, newName: string) => Promise<boolean>;
      getVersionStats: (versionId: string) => Promise<any>;
      importVersionFromFile: (filePath: string, versionId: string, versionName: string) => Promise<boolean>;
      exportVersion: (versionId: string, filePath: string) => Promise<boolean>;
      getDatabaseInfo: () => Promise<any>;
      // 번역본 표시 이름 관리
      getVersionDisplayNames: () => Promise<any[]>;
      setVersionDisplayName: (versionId: string, displayName: string) => Promise<boolean>;
      removeVersionDisplayName: (versionId: string) => Promise<boolean>;
      // 프롬프트 관리 API
      getPrompts: () => Promise<any[]>;
      getPrompt: (promptId: string) => Promise<any>;
      updatePrompt: (promptId: string, content: string) => Promise<boolean>;
      resetPrompt: (promptId: string) => Promise<boolean>;
    };
  }
}

export {};

// 성경 관련 타입들
export interface Book {
  id: number;
  korean_name: string;
  english_name: string;
  testament: string;
  chapters: number;
  book_order: number;
}

export interface Chapter {
  book: string;
  chapter: number;
  verses: number;
}

export interface Verse {
  id: number;
  book: string;
  chapter: number;
  verse: number;
  text: string;
  version: string;
  book_order?: number;
}

export interface Commentary {
  id: number;
  book: string;
  chapter: number;
  verse_start: number;
  verse_end: number;
  content: string;
  author: string;
}

// 기존 타입들 (호환성을 위해 유지)
export interface BibleVerse extends Verse {}

export interface SermonTopic {
  title: string;
  description: string;
}

export interface SermonOutline {
  title: string;
  parts: string[];
}

export interface SermonData {
  id?: string;
  bibleReference: {
    book: string;
    chapter: number;
    verseStart: number;
    verseEnd?: number;
  };
  topic: string;
  outline: SermonOutline;
  content: { [key: string]: string };
  createdAt: Date;
  updatedAt: Date;
}

// AI 설정 관련 타입들
export interface AIProvider {
  id: string;
  name: string;
  models: AIModel[];
  requiresApiKey: boolean;
  apiKeyLabel: string;
  baseUrl?: string;
}

export interface AIModel {
  id: string;
  name: string;
  description: string;
  maxTokens: number;
  isFree: boolean;
  costPerToken?: number;
}

export interface AISettings {
  provider: string;
  model: string;
  apiKey: string;
  temperature: number;
  maxTokens: number;
  systemPrompt: string;
  baseUrl?: string;
}

export interface CustomOutlineTemplate {
  id: string;
  name: string;
  parts: string[];
  createdAt: Date;
}

export interface AppSettings {
  ai: AISettings;
  theme: 'light' | 'dark' | 'system';
  language: 'ko' | 'en';
  autoSave: boolean;
  fontSize: 'small' | 'medium' | 'large';
  customOutlines: CustomOutlineTemplate[];
} 