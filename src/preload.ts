import { contextBridge, ipcRenderer } from 'electron';

// Define the API that will be exposed to the renderer process
const electronAPI = {
  // Bible data operations
  getBibleBooks: () => 
    ipcRenderer.invoke('get-bible-books'),
  
  getBibleVerses: (book: string, chapter: number, version?: string) => 
    ipcRenderer.invoke('get-bible-verses', book, chapter, version),
  
  getBibleVerse: (book: string, chapter: number, verse: number, version?: string) => 
    ipcRenderer.invoke('get-bible-verse', book, chapter, verse, version),
  
  getCommentaries: (book: string, chapter: number) => 
    ipcRenderer.invoke('get-commentaries', book, chapter),
  
  searchVerses: (query: string, version?: string) => 
    ipcRenderer.invoke('search-verses', query, version),
  
  // AI operations
  generateSermonTopics: (verseText: string) => 
    ipcRenderer.invoke('generate-sermon-topics', verseText),
  
  generateSermonDraft: (data: any) => 
    ipcRenderer.invoke('generate-sermon-draft', data),
  
  // File operations
  saveSermon: (sermonData: any) => 
    ipcRenderer.invoke('save-sermon', sermonData),
  
  loadSermon: (filePath: string) => 
    ipcRenderer.invoke('load-sermon', filePath),

  // 개발자 API - 번역본 관리
  getVersions: () => 
    ipcRenderer.invoke('get-versions'),
  
  deleteVersion: (versionId: string) => 
    ipcRenderer.invoke('delete-version', versionId),
  
  updateVersionName: (oldVersionId: string, newVersionId: string) => 
    ipcRenderer.invoke('update-version-name', oldVersionId, newVersionId),
  
  getVersionStats: (versionId: string) => 
    ipcRenderer.invoke('get-version-stats', versionId),
  
  getDatabaseInfo: () => 
    ipcRenderer.invoke('get-database-info'),
  
  addVersion: (versionData: any) => 
    ipcRenderer.invoke('add-version', versionData),

  // 번역본 표시 이름 관리
  getVersionDisplayNames: () => 
    ipcRenderer.invoke('get-version-display-names'),
  
  setVersionDisplayName: (versionId: string, displayName: string) => 
    ipcRenderer.invoke('set-version-display-name', versionId, displayName),
  
  removeVersionDisplayName: (versionId: string) => 
    ipcRenderer.invoke('remove-version-display-name', versionId),

  // 프롬프트 관리 API
  getPrompts: () => 
    ipcRenderer.invoke('get-prompts'),
  
  getPrompt: (promptId: string) => 
    ipcRenderer.invoke('get-prompt', promptId),
  
  updatePrompt: (promptId: string, content: string) => 
    ipcRenderer.invoke('update-prompt', promptId, content),
  
  resetPrompt: (promptId: string) => 
    ipcRenderer.invoke('reset-prompt', promptId),
};

// Expose the API to the renderer process
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// Types for the exposed API
export type ElectronAPI = typeof electronAPI; 