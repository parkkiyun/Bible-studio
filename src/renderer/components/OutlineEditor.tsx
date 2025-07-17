import React, { useState, useEffect } from 'react';
import { getAIService } from '../services/aiService';
import { SermonOutline, CustomOutlineTemplate, AppSettings } from '../../types/global';

interface OutlineEditorProps {
  selectedTopic: string;
  selectedVerse: { book: string; chapter: number; verse: number; text: string } | null;
  onOutlineComplete: (outline: SermonOutline) => void;
  darkMode: boolean;
}

const OutlineEditor: React.FC<OutlineEditorProps> = ({ 
  selectedTopic, 
  selectedVerse, 
  onOutlineComplete, 
  darkMode 
}) => {
  const [outline, setOutline] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [customOutline, setCustomOutline] = useState<string[]>(['']);
  const [customTemplates, setCustomTemplates] = useState<CustomOutlineTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');

  useEffect(() => {
    loadCustomTemplates();
  }, []);

  const loadCustomTemplates = () => {
    try {
      const savedSettings = localStorage.getItem('appSettings');
      if (savedSettings) {
        const settings: AppSettings = JSON.parse(savedSettings);
        setCustomTemplates(settings.customOutlines || []);
      }
    } catch (error) {
      console.error('커스텀 템플릿 로드 실패:', error);
    }
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
    buttonDanger: darkMode 
      ? 'bg-red-600 hover:bg-red-700 text-white' 
      : 'bg-red-600 hover:bg-red-700 text-white',
    input: darkMode 
      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500',
    outlineItem: darkMode 
      ? 'bg-gray-700 hover:bg-gray-600 text-white border-gray-600' 
      : 'bg-gray-50 hover:bg-gray-100 text-gray-700 border-gray-200'
  };

  const generateOutline = async () => {
    if (!selectedVerse || !selectedTopic) return;

    setLoading(true);
    try {
      const savedSettings = localStorage.getItem('appSettings');
      if (!savedSettings) {
        throw new Error('AI 설정이 필요합니다. 설정 페이지에서 AI를 구성해주세요.');
      }
      
      const settings = JSON.parse(savedSettings);
      const aiService = getAIService(settings.ai);
      
      const verseText = `${selectedVerse.book} ${selectedVerse.chapter}:${selectedVerse.verse} - ${selectedVerse.text}`;
      const generatedOutline = await aiService.generateOutline(verseText, selectedTopic);
      setOutline(generatedOutline);
    } catch (error) {
      console.error('목차 생성 실패:', error);
      alert('목차 생성에 실패했습니다. 설정에서 AI 연결을 확인해주세요.');
    } finally {
      setLoading(false);
    }
  };

  const addCustomOutlineItem = () => {
    setCustomOutline([...customOutline, '']);
  };

  const removeCustomOutlineItem = (index: number) => {
    setCustomOutline(customOutline.filter((_, i) => i !== index));
  };

  const updateCustomOutlineItem = (index: number, value: string) => {
    const newOutline = [...customOutline];
    newOutline[index] = value;
    setCustomOutline(newOutline);
  };

  const handleOutlineSelect = (selectedOutline: string[]) => {
    const filteredOutline = selectedOutline.filter(item => item.trim() !== '');
    if (filteredOutline.length > 0) {
      onOutlineComplete({
        title: selectedTopic,
        parts: filteredOutline
      });
    }
  };

  const handleCustomOutlineSubmit = () => {
    const filteredOutline = customOutline.filter(item => item.trim() !== '');
    if (filteredOutline.length > 0) {
      handleOutlineSelect(filteredOutline);
    }
  };

  const handleTemplateSelect = (templateId: string) => {
    setSelectedTemplate(templateId);
    const template = customTemplates.find(t => t.id === templateId);
    if (template) {
      setCustomOutline([...template.parts]);
    }
  };

  const resetCustomOutline = () => {
    setCustomOutline(['']);
    setSelectedTemplate('');
  };

  return (
    <div className={`p-6 rounded-lg border shadow-lg ${themeClasses.container}`}>
      <h2 className="text-xl font-bold mb-4">3단계: 설교 목차 작성</h2>
      
      {selectedTopic && selectedVerse ? (
        <div className={`p-4 rounded-lg border mb-6 ${themeClasses.card}`}>
          <h3 className="font-semibold mb-2">설교 정보</h3>
          <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            본문: {selectedVerse.book} {selectedVerse.chapter}:{selectedVerse.verse}
          </p>
          <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'} mt-1`}>
            주제: {selectedTopic}
          </p>
        </div>
      ) : (
        <div className={`p-4 rounded-lg border mb-6 ${darkMode ? 'bg-yellow-900 border-yellow-700 text-yellow-100' : 'bg-yellow-50 border-yellow-200 text-yellow-800'}`}>
          <p>먼저 성경 구절과 주제를 선택해주세요.</p>
        </div>
      )}

      <div className="space-y-6">
        {/* AI 목차 생성 */}
        <div>
          <h3 className="font-semibold mb-3">AI 목차 생성</h3>
          <button
            onClick={generateOutline}
            disabled={!selectedVerse || !selectedTopic || loading}
            className={`w-full py-3 px-4 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${themeClasses.button}`}
          >
            {loading ? '목차 생성 중...' : 'AI 목차 생성'}
          </button>

          {outline.length > 0 && (
            <div className="mt-4">
              <h4 className="font-medium mb-2">생성된 목차</h4>
              <div className="space-y-2">
                {outline.map((item, index) => (
                  <div key={index} className={`p-3 rounded-lg border ${themeClasses.outlineItem}`}>
                    <div className="flex items-center gap-2">
                      <span className={`font-medium ${darkMode ? 'text-blue-300' : 'text-blue-600'}`}>
                        {index + 1}.
                      </span>
                      <span>{item}</span>
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={() => handleOutlineSelect(outline)}
                className={`w-full mt-4 py-2 px-4 rounded-lg font-medium transition-colors ${themeClasses.button}`}
              >
                이 목차 사용하기
              </button>
            </div>
          )}
        </div>

        {/* 템플릿 목차 선택 */}
        {customTemplates.length > 0 && (
          <div>
            <h3 className="font-semibold mb-3">저장된 목차 템플릿</h3>
            <div className="mb-4">
              <select
                value={selectedTemplate}
                onChange={(e) => handleTemplateSelect(e.target.value)}
                className={`w-full px-3 py-2 rounded-lg border ${themeClasses.input}`}
              >
                <option value="">템플릿을 선택하세요</option>
                {customTemplates.map(template => (
                  <option key={template.id} value={template.id}>
                    {template.name} ({template.parts.length}개 항목)
                  </option>
                ))}
              </select>
            </div>
            
            {selectedTemplate && (
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">선택된 템플릿 미리보기</h4>
                  <button
                    onClick={resetCustomOutline}
                    className={`text-sm px-2 py-1 rounded ${themeClasses.buttonSecondary}`}
                  >
                    초기화
                  </button>
                </div>
                <div className="space-y-1 p-3 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700">
                  {customTemplates.find(t => t.id === selectedTemplate)?.parts.map((part, index) => (
                    <div key={index} className="text-sm">
                      {index + 1}. {part}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 수동 목차 작성 */}
        <div>
          <h3 className="font-semibold mb-3">직접 목차 작성</h3>
          <div className="space-y-3">
            {customOutline.map((item, index) => (
              <div key={index} className="flex gap-2">
                <div className="flex items-center justify-center w-8 h-10 rounded border border-gray-300">
                  <span className={`text-sm font-medium ${darkMode ? 'text-blue-300' : 'text-blue-600'}`}>
                    {index + 1}
                  </span>
                </div>
                <input
                  type="text"
                  value={item}
                  onChange={(e) => updateCustomOutlineItem(index, e.target.value)}
                  placeholder={`${index + 1}번째 항목을 입력하세요`}
                  className={`flex-1 px-3 py-2 rounded-lg border ${themeClasses.input}`}
                />
                {customOutline.length > 1 && (
                  <button
                    onClick={() => removeCustomOutlineItem(index)}
                    className={`px-3 py-2 rounded-lg transition-colors ${themeClasses.buttonDanger}`}
                  >
                    삭제
                  </button>
                )}
              </div>
            ))}
          </div>

          <div className="flex gap-2 mt-4">
            <button
              onClick={addCustomOutlineItem}
              className={`px-4 py-2 rounded-lg border transition-colors ${themeClasses.buttonSecondary}`}
            >
              항목 추가
            </button>
            <button
              onClick={handleCustomOutlineSubmit}
              disabled={customOutline.filter(item => item.trim()).length === 0}
              className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${themeClasses.button}`}
            >
              목차 완성
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OutlineEditor; 