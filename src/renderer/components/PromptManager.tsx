import React, { useState, useEffect } from 'react';

interface Prompt {
  id: string;
  name: string;
  category: string;
  description: string;
  content: string;
  variables?: string[];
}

interface PromptManagerProps {
  darkMode: boolean;
}



const PromptManager: React.FC<PromptManagerProps> = ({ darkMode }) => {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [editContent, setEditContent] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [hasChanges, setHasChanges] = useState(false);

  const themeClasses = {
    container: darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-900',
    card: darkMode ? 'bg-gray-800 border-gray-700' : 'bg-gray-50 border-gray-200',
    input: darkMode ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' : 'bg-white border-gray-300 text-gray-900',
    button: darkMode ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'bg-blue-500 hover:bg-blue-600 text-white',
    secondaryButton: darkMode ? 'bg-gray-600 hover:bg-gray-700 text-white' : 'bg-gray-500 hover:bg-gray-600 text-white',
    dangerButton: darkMode ? 'bg-red-600 hover:bg-red-700 text-white' : 'bg-red-500 hover:bg-red-600 text-white',
    sidebar: darkMode ? 'bg-gray-800 border-gray-700' : 'bg-gray-100 border-gray-200',
    listItem: darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-200',
    selectedItem: darkMode ? 'bg-blue-800' : 'bg-blue-100'
  };

  useEffect(() => {
    loadPrompts();
  }, []);

  useEffect(() => {
    if (selectedPrompt) {
      setEditContent(selectedPrompt.content);
      setHasChanges(false);
    }
  }, [selectedPrompt]);

  const loadPrompts = async () => {
    try {
      const promptsData = await window.electronAPI.getPrompts();
      setPrompts(promptsData);
    } catch (error) {
      console.error('프롬프트 로드 실패:', error);
      setPrompts([]);
    }
  };

  const handleSave = async () => {
    if (!selectedPrompt) return;

    try {
      const success = await window.electronAPI.updatePrompt(selectedPrompt.id, editContent);
      if (success) {
        // 프롬프트 목록 새로고침
        await loadPrompts();
        // 현재 선택된 프롬프트 업데이트
        setSelectedPrompt({ ...selectedPrompt, content: editContent });
        setHasChanges(false);
        alert('프롬프트가 저장되었습니다!');
      } else {
        alert('프롬프트 저장에 실패했습니다.');
      }
    } catch (error) {
      console.error('프롬프트 저장 실패:', error);
      alert('프롬프트 저장 중 오류가 발생했습니다.');
    }
  };

  const handleReset = async (promptId: string) => {
    if (!confirm('이 프롬프트를 원래 상태로 초기화하시겠습니까?')) {
      return;
    }

    try {
      const success = await window.electronAPI.resetPrompt(promptId);
      if (success) {
        // 프롬프트 목록 새로고침
        await loadPrompts();
        // 현재 선택된 프롬프트가 초기화된 프롬프트라면 업데이트
        if (selectedPrompt?.id === promptId) {
          const resetPrompt = await window.electronAPI.getPrompt(promptId);
          if (resetPrompt) {
            setSelectedPrompt(resetPrompt);
            setEditContent(resetPrompt.content);
            setHasChanges(false);
          }
        }
        alert('프롬프트가 초기화되었습니다.');
      } else {
        alert('프롬프트 초기화에 실패했습니다.');
      }
    } catch (error) {
      console.error('프롬프트 초기화 실패:', error);
      alert('프롬프트 초기화 중 오류가 발생했습니다.');
    }
  };

  const handleContentChange = (value: string) => {
    setEditContent(value);
    setHasChanges(selectedPrompt ? value !== selectedPrompt.content : false);
  };

  const filteredPrompts = prompts.filter(prompt => {
    const matchesSearch = prompt.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      prompt.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || prompt.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = ['all', ...Array.from(new Set(prompts.map(p => p.category)))];

  return (
    <div className={`h-full flex ${themeClasses.container}`}>
      {/* 사이드바 */}
      <div className={`w-1/3 border-r ${themeClasses.sidebar}`}>
        <div className="p-4">
          <h2 className="text-xl font-bold mb-4">실제 프롬프트 관리</h2>
          
          {/* 검색 */}
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="프롬프트 검색..."
            className={`w-full p-2 rounded border mb-4 ${themeClasses.input}`}
          />

          {/* 카테고리 필터 */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className={`w-full p-2 rounded border mb-4 ${themeClasses.input}`}
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category === 'all' ? '모든 카테고리' : category}
              </option>
            ))}
          </select>
        </div>

        {/* 프롬프트 목록 */}
        <div className="overflow-y-auto">
          {filteredPrompts.map(prompt => (
            <div
              key={prompt.id}
              onClick={() => setSelectedPrompt(prompt)}
              className={`p-4 border-b cursor-pointer transition-colors ${themeClasses.listItem} ${
                selectedPrompt?.id === prompt.id ? themeClasses.selectedItem : ''
              }`}
            >
              <div className="font-medium">{prompt.name}</div>
              <div className="text-sm opacity-70">{prompt.category}</div>
              <div className="text-xs opacity-60 mt-1">{prompt.description}</div>
              {prompt.variables && prompt.variables.length > 0 && (
                <div className="text-xs mt-2">
                  <span className="opacity-70">변수: </span>
                  {prompt.variables.map(variable => (
                    <span key={variable} className="bg-blue-500 text-white px-1 py-0.5 rounded text-xs mr-1">
                      {variable}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 메인 편집 영역 */}
      <div className="flex-1 flex flex-col">
        {selectedPrompt ? (
          <>
            {/* 헤더 */}
            <div className={`p-6 border-b ${themeClasses.card}`}>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-2xl font-bold">{selectedPrompt.name}</h3>
                  <p className="text-sm opacity-70 mt-1">{selectedPrompt.description}</p>
                  <span className={`inline-block px-2 py-1 rounded text-xs mt-2 ${themeClasses.secondaryButton}`}>
                    {selectedPrompt.category}
                  </span>
                  {selectedPrompt.variables && selectedPrompt.variables.length > 0 && (
                    <div className="mt-2">
                      <span className="text-sm opacity-70">사용 가능한 변수: </span>
                      {selectedPrompt.variables.map(variable => (
                        <span key={variable} className="bg-green-500 text-white px-2 py-1 rounded text-xs mr-1">
                          {`{${variable}}`}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleReset(selectedPrompt.id)}
                    className={`px-4 py-2 rounded transition-colors ${themeClasses.secondaryButton}`}
                  >
                    초기화
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={!hasChanges}
                    className={`px-4 py-2 rounded transition-colors ${
                      hasChanges ? themeClasses.button : 'bg-gray-400 cursor-not-allowed'
                    }`}
                  >
                    {hasChanges ? '저장' : '저장됨'}
                  </button>
                </div>
              </div>
            </div>

            {/* 편집 영역 */}
            <div className="flex-1 p-6">
              <div className="h-full">
                <label className="block text-sm font-medium mb-2">
                  프롬프트 내용
                  {hasChanges && <span className="text-yellow-500 ml-2">● 변경됨</span>}
                </label>
                <textarea
                  value={editContent}
                  onChange={(e) => handleContentChange(e.target.value)}
                  placeholder="프롬프트 내용을 입력하세요..."
                  className={`w-full h-full p-4 rounded border resize-none ${themeClasses.input}`}
                />
              </div>
            </div>

            {/* 미리보기 */}
            <div className={`p-4 border-t ${themeClasses.card}`}>
              <h4 className="font-medium mb-2">현재 내용 미리보기:</h4>
              <div className="text-sm opacity-80 max-h-20 overflow-y-auto">
                {editContent || selectedPrompt.content}
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <p className="text-lg">프롬프트를 선택하세요</p>
              <p className="text-sm mt-2">왼쪽에서 편집하고 싶은 프롬프트를 클릭하세요</p>
              <p className="text-xs mt-4 opacity-70">
                ⚠️ 이 프롬프트들은 실제 AI 서비스에서 사용됩니다
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PromptManager; 