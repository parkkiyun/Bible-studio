import React, { useState } from 'react';
import { getAIService } from '../services/aiService';

interface TopicSelectorProps {
  selectedVerse: { book: string; chapter: number; verse: number; text: string } | null;
  onTopicSelect: (topic: string) => void;
  darkMode: boolean;
}

const TopicSelector: React.FC<TopicSelectorProps> = ({ selectedVerse, onTopicSelect, darkMode }) => {
  const [topics, setTopics] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [customTopic, setCustomTopic] = useState('');

  // 마크다운 볼드체를 HTML로 변환하는 함수
  const formatText = (text: string) => {
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  };

  const themeClasses = {
    container: darkMode 
      ? 'bg-gray-900 text-white border-gray-700' 
      : 'bg-white text-gray-900 border-gray-200',
    card: darkMode 
      ? 'bg-gray-800 border-gray-700' 
      : 'bg-white border-gray-200',
    button: darkMode 
      ? 'bg-blue-600 hover:bg-blue-700 text-white' 
      : 'bg-blue-600 hover:bg-blue-700 text-white',
    buttonSecondary: darkMode 
      ? 'bg-gray-700 hover:bg-gray-600 text-white border-gray-600' 
      : 'bg-white hover:bg-gray-50 text-gray-700 border-gray-300',
    input: darkMode 
      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500',
    topicButton: darkMode 
      ? 'bg-gray-700 hover:bg-gray-600 text-white border-gray-600' 
      : 'bg-gray-50 hover:bg-gray-100 text-gray-700 border-gray-200'
  };

  const generateTopics = async () => {
    if (!selectedVerse) return;

    setLoading(true);
    try {
      // 설정에서 AI 서비스 가져오기
      const savedSettings = localStorage.getItem('appSettings');
      if (!savedSettings) {
        throw new Error('AI 설정이 필요합니다. 설정 페이지에서 AI를 구성해주세요.');
      }
      
      const settings = JSON.parse(savedSettings);
      console.log('AI 설정:', settings.ai);
      
      const aiService = getAIService(settings.ai);
      
      const verseText = `${selectedVerse.book} ${selectedVerse.chapter}:${selectedVerse.verse} - ${selectedVerse.text}`;
      console.log('구절 텍스트:', verseText);
      
      console.log('AI 주제 생성 시작...');
      const generatedTopics = await aiService.generateTopics(verseText);
      console.log('생성된 주제들:', generatedTopics);
      
      if (generatedTopics && generatedTopics.length > 0) {
        setTopics(generatedTopics);
        console.log('AI 생성 주제 사용:', generatedTopics);
      } else {
        console.log('AI에서 주제를 생성하지 못했습니다. 빈 배열 설정.');
        setTopics([]);
        alert('AI에서 주제를 생성하지 못했습니다. 직접 입력하거나 다시 시도해주세요.');
      }
    } catch (error) {
      console.error('주제 생성 실패:', error);
      
      // 에러 발생 시 빈 배열 설정
      setTopics([]);
      
      // 사용자에게 더 구체적인 에러 메시지 표시
      const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.';
      
      // 설정 다시 읽기 (에러 처리용)
      let aiProvider = 'unknown';
      let aiModel = 'unknown';
      try {
        const errorSavedSettings = localStorage.getItem('appSettings');
        if (errorSavedSettings) {
          const errorSettings = JSON.parse(errorSavedSettings);
          aiProvider = errorSettings.ai?.provider || 'unknown';
          aiModel = errorSettings.ai?.model || 'unknown';
        }
      } catch (e) {
        console.error('설정 파싱 실패:', e);
      }
      
              // Ollama 관련 특별 처리
        if (aiProvider === 'local') {
          if (errorMessage.includes('Failed to fetch') || errorMessage.includes('연결할 수 없습니다')) {
            alert(`Ollama AI 연결 실패!\n\n문제 해결 방법:\n1. Ollama가 설치되어 있는지 확인\n2. 터미널에서 'ollama serve' 실행\n3. 모델이 다운로드되어 있는지 확인 ('ollama pull ${aiModel}')\n\n직접 주제를 입력하거나 다시 시도해주세요.`);
          } else {
            alert(`Ollama AI 오류: ${errorMessage}\n\n직접 주제를 입력하거나 다시 시도해주세요.`);
          }
        } else {
          alert(`AI 주제 생성에 실패했습니다: ${errorMessage}\n\n직접 주제를 입력하거나 다시 시도해주세요.`);
        }
    } finally {
      setLoading(false);
    }
  };

  const handleTopicSelect = (topic: string) => {
    onTopicSelect(topic);
  };

  const handleCustomTopicSubmit = () => {
    if (customTopic.trim()) {
      onTopicSelect(customTopic.trim());
      setCustomTopic('');
    }
  };

  return (
    <div className={`p-6 rounded-lg border shadow-lg ${themeClasses.container}`}>
      <h2 className="text-xl font-bold mb-4">2단계: 설교 주제 선택</h2>
      
      {selectedVerse ? (
        <div className={`p-4 rounded-lg border mb-6 ${themeClasses.card}`}>
          <h3 className="font-semibold mb-2">선택된 말씀</h3>
          <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            {selectedVerse.book} {selectedVerse.chapter}:{selectedVerse.verse}
          </p>
          <p className="mt-2">{selectedVerse.text}</p>
        </div>
      ) : (
        <div className={`p-4 rounded-lg border mb-6 ${darkMode ? 'bg-yellow-900 border-yellow-700 text-yellow-100' : 'bg-yellow-50 border-yellow-200 text-yellow-800'}`}>
          <p>먼저 성경 구절을 선택해주세요.</p>
        </div>
      )}

      <div className="space-y-4">
        <div>
          <button
            onClick={generateTopics}
            disabled={!selectedVerse || loading}
            className={`w-full py-3 px-4 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${themeClasses.button}`}
          >
            {loading ? '주제 생성 중...' : 'AI 주제 추천 받기'}
          </button>
        </div>

        {topics.length > 0 && (
          <div>
            <h3 className="font-semibold mb-3">추천 주제</h3>
            <div className="space-y-2">
              {topics.map((topic, index) => (
                <button
                  key={index}
                  onClick={() => handleTopicSelect(topic)}
                  className={`w-full p-3 text-left rounded-lg border transition-colors ${themeClasses.topicButton}`}
                >
                  <div 
                    dangerouslySetInnerHTML={{ __html: formatText(topic) }}
                    className="leading-relaxed"
                  />
                </button>
              ))}
            </div>
          </div>
        )}

        <div>
          <h3 className="font-semibold mb-3">직접 입력</h3>
          <div className="flex gap-2">
            <input
              type="text"
              value={customTopic}
              onChange={(e) => setCustomTopic(e.target.value)}
              placeholder="설교 주제를 입력하세요"
              className={`flex-1 px-3 py-2 rounded-lg border ${themeClasses.input}`}
              onKeyPress={(e) => e.key === 'Enter' && handleCustomTopicSubmit()}
            />
            <button
              onClick={handleCustomTopicSubmit}
              disabled={!customTopic.trim()}
              className={`px-4 py-2 rounded-lg border transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${themeClasses.buttonSecondary}`}
            >
              선택
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopicSelector; 