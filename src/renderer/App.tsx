import React, { useState, useEffect } from 'react';
import BibleViewer from './components/BibleViewer';
import BibleSelector from './components/BibleSelector';
import TopicSelector from './components/TopicSelector';
import OutlineEditor from './components/OutlineEditor';
import SermonEditor from './components/SermonEditor';
import Settings from './components/Settings';
import DeveloperPage from './components/DeveloperPage';
import { AppSettings, SermonOutline } from '../types/global';

type Step = 'bible' | 'topic' | 'outline' | 'editor';
type Page = 'main' | 'developer';

const App: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);
  const [showSettings, setShowSettings] = useState<boolean>(false);
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [isResizing, setIsResizing] = useState<boolean>(false);
  const [panelSizes, setPanelSizes] = useState({ bible: 40, sermon: 60 });
  
  // 페이지 상태
  const [currentPage, setCurrentPage] = useState<Page>('main');
  
  // 패널 표시 상태
  const [showBibleViewer, setShowBibleViewer] = useState<boolean>(true);
  const [showSermonAssistant, setShowSermonAssistant] = useState<boolean>(true);
  
  // 설교문 작성 상태
  const [currentStep, setCurrentStep] = useState<Step>('bible');
  const [selectedVerse, setSelectedVerse] = useState<{ book: string; chapter: number; verse: number; text: string } | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<string>('');
  const [sermonOutline, setSermonOutline] = useState<SermonOutline | null>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  // 다크모드 적용
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const loadSettings = async () => {
    try {
      const savedSettings = localStorage.getItem('appSettings');
      if (savedSettings) {
        const parsedSettings = JSON.parse(savedSettings);
        setSettings(parsedSettings);
        setIsDarkMode(parsedSettings.theme === 'dark');
      }
    } catch (error) {
      console.error('설정 로드 실패:', error);
    }
  };

  const handleVerseSelect = (verse: { book: string; chapter: number; verse: number; text: string }) => {
    setSelectedVerse(verse);
    setCurrentStep('topic');
  };

  const handleTopicSelect = (topic: string) => {
    setSelectedTopic(topic);
    setCurrentStep('outline');
  };

  const handleOutlineComplete = (outline: SermonOutline) => {
    setSermonOutline(outline);
    setCurrentStep('editor');
  };

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  const handleSettingsClose = () => {
    setShowSettings(false);
    loadSettings();
  };

  // 패널 크기 조절 핸들러
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsResizing(true);
    e.preventDefault();
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isResizing) return;
    
    const container = document.getElementById('main-container');
    if (!container) return;
    
    const rect = container.getBoundingClientRect();
    const newBibleWidth = ((e.clientX - rect.left) / rect.width) * 100;
    
    if (newBibleWidth >= 20 && newBibleWidth <= 80) {
      setPanelSizes({
        bible: newBibleWidth,
        sermon: 100 - newBibleWidth
      });
    }
  };

  const handleMouseUp = () => {
    setIsResizing(false);
  };

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isResizing]);

  // 수정된 패널 토글 함수들
  const toggleBibleViewer = () => {
    if (showBibleViewer && !showSermonAssistant) {
      // 성경 뷰어만 켜져있을 때 끄면 AI 도우미 켜기
      setShowBibleViewer(false);
      setShowSermonAssistant(true);
    } else {
      setShowBibleViewer(!showBibleViewer);
    }
  };

  const toggleSermonAssistant = () => {
    if (showSermonAssistant && !showBibleViewer) {
      // AI 도우미만 켜져있을 때 끄면 성경 뷰어 켜기
      setShowSermonAssistant(false);
      setShowBibleViewer(true);
    } else {
      setShowSermonAssistant(!showSermonAssistant);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <div className="h-full flex flex-col">
        {/* Header - 라이트 모드 색상 완전 수정 */}
        <header className="flex-shrink-0 bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
          <div className="px-6 py-4 flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                바이블 스튜디오
              </h1>
              
              {/* 패널 토글 버튼들 */}
              <div className="flex items-center space-x-2 ml-8">
                <button
                  onClick={toggleBibleViewer}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    showBibleViewer
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                  title="성경 뷰어 토글"
                >
                  📖 성경 뷰어
                </button>
                
                <button
                  onClick={toggleSermonAssistant}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    showSermonAssistant
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                  title="AI 설교문 도우미 토글"
                >
                  🤖 AI 도우미
                </button>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Developer Tools Button */}
              <button
                onClick={() => setCurrentPage(currentPage === 'developer' ? 'main' : 'developer')}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentPage === 'developer'
                    ? 'bg-orange-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
                title="개발자 도구"
              >
                🛠️ 개발자
              </button>

              {/* Settings Button */}
              <button
                onClick={() => setShowSettings(true)}
                className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-gray-700 dark:text-gray-300"
                title="설정"
              >
                ⚙️
              </button>

              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-gray-700 dark:text-gray-300"
                title={isDarkMode ? '라이트 모드' : '다크 모드'}
              >
                {isDarkMode ? '🌞' : '🌙'}
              </button>
              
              {/* AI Status Indicator */}
              {settings && (
                <div className="flex items-center space-x-2 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-gray-600 dark:text-gray-400">
                    {settings.ai.provider === 'google' && 'Google AI'}
                    {settings.ai.provider === 'openai' && 'OpenAI'}
                    {settings.ai.provider === 'anthropic' && 'Claude'}
                    {settings.ai.provider === 'local' && 'Local AI'}
                  </span>
                </div>
              )}


            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 flex overflow-hidden" id="main-container">
          {/* 개발자 페이지 */}
          {currentPage === 'developer' && (
            <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900">
              <DeveloperPage darkMode={isDarkMode} />
            </div>
          )}

          {/* 메인 페이지 */}
          {currentPage === 'main' && (
            <>
          {/* Bible Viewer Panel */}
          {showBibleViewer && (
            <div 
              className="border-r border-gray-300 dark:border-gray-600 flex flex-col"
              style={{ width: showSermonAssistant ? `${panelSizes.bible}%` : '100%' }}
            >
              <BibleViewer 
                onVerseSelect={handleVerseSelect}
                darkMode={isDarkMode}
              />
            </div>
          )}

          {/* Resizer */}
          {showBibleViewer && showSermonAssistant && (
            <div
              className="w-1 bg-gray-300 dark:bg-gray-600 cursor-col-resize hover:bg-gray-400 dark:hover:bg-gray-500 transition-colors flex items-center justify-center"
              onMouseDown={handleMouseDown}
            >
              <div className="w-0.5 h-8 bg-gray-400 dark:bg-gray-500 rounded-full"></div>
            </div>
          )}

          {/* Sermon Assistant Panel - 배경색 완전 수정 */}
          {showSermonAssistant && (
            <div 
              className="flex-1 overflow-y-auto bg-white dark:bg-gray-900"
              style={{ width: showBibleViewer ? `${100 - panelSizes.bible}%` : '100%' }}
            >
              <div className="bg-white dark:bg-gray-900 min-h-full">
                {/* AI 도우미 단계 네비게이션 */}
                <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
                  <div className="flex items-center justify-between">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                      AI 설교문 도우미
                    </h2>
                    <div className="flex items-center space-x-2 text-sm">
                      <button
                        onClick={() => setCurrentStep('bible')}
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          currentStep === 'bible' 
                            ? 'bg-blue-600 text-white' 
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                        }`}
                      >
                        1. 본문 선택
                      </button>
                      <div className="text-gray-400 dark:text-gray-500">→</div>
                      <button
                        onClick={() => selectedVerse ? setCurrentStep('topic') : null}
                        disabled={!selectedVerse}
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          currentStep === 'topic' 
                            ? 'bg-blue-600 text-white' 
                            : selectedVerse 
                              ? 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                              : 'bg-gray-50 dark:bg-gray-800 text-gray-400 dark:text-gray-600 cursor-not-allowed'
                        }`}
                      >
                        2. 주제 선택
                      </button>
                      <div className="text-gray-400 dark:text-gray-500">→</div>
                      <button
                        onClick={() => selectedTopic ? setCurrentStep('outline') : null}
                        disabled={!selectedTopic}
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          currentStep === 'outline' 
                            ? 'bg-blue-600 text-white' 
                            : selectedTopic 
                              ? 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                              : 'bg-gray-50 dark:bg-gray-800 text-gray-400 dark:text-gray-600 cursor-not-allowed'
                        }`}
                      >
                        3. 목차 구성
                      </button>
                      <div className="text-gray-400 dark:text-gray-500">→</div>
                      <button
                        onClick={() => sermonOutline ? setCurrentStep('editor') : null}
                        disabled={!sermonOutline}
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          currentStep === 'editor' 
                            ? 'bg-blue-600 text-white' 
                            : sermonOutline 
                              ? 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                              : 'bg-gray-50 dark:bg-gray-800 text-gray-400 dark:text-gray-600 cursor-not-allowed'
                        }`}
                      >
                        4. 초안 작성
                      </button>
                    </div>
                  </div>
                </div>

                {/* AI 도우미 콘텐츠 */}
                <div className="p-6">
                  {currentStep === 'bible' && (
                    <BibleSelector 
                      onVerseSelect={handleVerseSelect}
                      darkMode={isDarkMode}
                    />
                  )}
                  
                  {currentStep === 'topic' && selectedVerse && (
                    <TopicSelector
                      selectedVerse={selectedVerse}
                      onTopicSelect={handleTopicSelect}
                      darkMode={isDarkMode}
                    />
                  )}
                  
                  {currentStep === 'outline' && selectedTopic && selectedVerse && (
                    <OutlineEditor
                      selectedTopic={selectedTopic}
                      selectedVerse={selectedVerse}
                      onOutlineComplete={handleOutlineComplete}
                      darkMode={isDarkMode}
                    />
                  )}
                  
                  {currentStep === 'editor' && selectedTopic && sermonOutline && selectedVerse && (
                    <SermonEditor
                      selectedVerse={selectedVerse}
                      selectedTopic={selectedTopic}
                      outline={sermonOutline}
                      darkMode={isDarkMode}
                    />
                  )}
                </div>
              </div>
            </div>
          )}

          {/* 둘 다 꺼진 경우 메시지 */}
          {!showBibleViewer && !showSermonAssistant && (
            <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
              <div className="text-center text-gray-500 dark:text-gray-400">
                <div className="text-6xl mb-4">📖</div>
                <h2 className="text-2xl font-bold mb-2 text-gray-900 dark:text-white">바이블 스튜디오</h2>
                <p className="mb-4">성경 뷰어 또는 AI 설교문 도우미를 활성화하세요.</p>
                <div className="space-x-4">
                  <button
                    onClick={() => setShowBibleViewer(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    📖 성경 뷰어 열기
                  </button>
                  <button
                    onClick={() => setShowSermonAssistant(true)}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    🤖 AI 도우미 열기
                  </button>
                </div>
              </div>
            </div>
          )}
            </>
          )}
        </main>

        {/* Settings Modal */}
        {showSettings && (
          <Settings onClose={handleSettingsClose} />
        )}
      </div>
    </div>
  );
};

export default App; 