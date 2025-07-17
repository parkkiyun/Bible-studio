import React, { useState, useEffect, useRef } from 'react';
import { SermonTopic, SermonOutline, AppSettings } from '../../types/global';
import { getAIService } from '../services/aiService';

interface SermonEditorProps {
  selectedVerse: { book: string; chapter: number; verse: number; text: string };
  selectedTopic: string;
  outline: SermonOutline;
  darkMode: boolean;
}

// 간단한 텍스트 에디터 컴포넌트
interface SimpleEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  minHeight?: string;
  darkMode: boolean;
}

const SimpleEditor: React.FC<SimpleEditorProps> = ({ 
  value, 
  onChange, 
  placeholder = '',
  minHeight = '200px',
  darkMode
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const insertText = (before: string, after: string = '') => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = value.substring(start, end);
    const newText = value.substring(0, start) + before + selectedText + after + value.substring(end);
    
    onChange(newText);
    
    // 커서 위치 조정
    setTimeout(() => {
      textarea.focus();
      const newCursorPos = start + before.length + selectedText.length + after.length;
      textarea.setSelectionRange(newCursorPos, newCursorPos);
    }, 0);
  };

  const formatButtons = [
    { label: 'B', title: '굵게', action: () => insertText('**', '**') },
    { label: 'I', title: '기울임', action: () => insertText('*', '*') },
    { label: 'H1', title: '제목 1', action: () => insertText('\n# ', '\n') },
    { label: 'H2', title: '제목 2', action: () => insertText('\n## ', '\n') },
    { label: 'H3', title: '제목 3', action: () => insertText('\n### ', '\n') },
    { label: '•', title: '목록', action: () => insertText('\n- ', '') },
    { label: '1.', title: '번호 목록', action: () => insertText('\n1. ', '') },
    { label: '""', title: '인용', action: () => insertText('\n> ', '\n') },
  ];

  return (
    <div className={`border rounded-lg overflow-hidden ${
      darkMode ? 'border-gray-600' : 'border-gray-300'
    }`}>
      {/* 툴바 */}
      <div className={`border-b p-2 flex flex-wrap gap-1 ${
        darkMode 
          ? 'bg-gray-700 border-gray-600' 
          : 'bg-gray-50 border-gray-300'
      }`}>
        {formatButtons.map((button, index) => (
          <button
            key={index}
            onClick={button.action}
            title={button.title}
            className={`px-2 py-1 text-sm font-medium rounded transition-colors ${
              darkMode
                ? 'text-gray-300 hover:bg-gray-600'
                : 'text-gray-700 hover:bg-gray-200'
            }`}
          >
            {button.label}
          </button>
        ))}
      </div>
      
      {/* 텍스트 영역 */}
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={`w-full p-4 resize-none focus:outline-none ${
          darkMode 
            ? 'bg-gray-800 text-white' 
            : 'bg-white text-gray-900'
        }`}
        style={{ minHeight }}
      />
    </div>
  );
};

const SermonEditor: React.FC<SermonEditorProps> = ({ selectedVerse, selectedTopic, outline, darkMode }) => {
  const [sermonContent, setSermonContent] = useState<{ [key: string]: string }>({});
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [currentEditingPart, setCurrentEditingPart] = useState<string>('');
  const [isGeneratingImage, setIsGeneratingImage] = useState<boolean>(false);
  const [currentImagePart, setCurrentImagePart] = useState<string>('');
  const [generatedImages, setGeneratedImages] = useState<{ [key: string]: string }>({});
  const [showImageModal, setShowImageModal] = useState<boolean>(false);
  const [currentViewingImage, setCurrentViewingImage] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  // 임시 설교문 생성 함수 (백업용)
  const generateMockSermon = (part: string): string => {
    const mockContent: { [key: string]: string } = {
      '서론: 하나님의 사랑의 크기': `# 서론: 하나님의 사랑의 크기

사랑하는 성도 여러분, 오늘 우리가 함께 나눌 말씀은 요한복음 3장 16절입니다. 이 말씀은 기독교 신앙의 핵심을 담고 있는 황금절이라고 불립니다.

**"하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니 이는 그를 믿는 자마다 멸망하지 않고 영생을 얻게 하려 하심이라"**

이 말씀을 통해 우리는 하나님의 사랑이 얼마나 크고 깊은지를 깨달을 수 있습니다. 하나님의 사랑은 조건부가 아니라 무조건적이며, 개인적이 아니라 보편적입니다.`,

      '본론 1: 독생자를 주신 사랑': `# 본론 1: 독생자를 주신 사랑

하나님의 사랑의 증거는 바로 독생자 예수 그리스도를 이 땅에 보내주신 것입니다. 이는 하나님께서 우리를 위해 치르신 최고의 대가였습니다.

하나님은 우리가 죄인 되었을 때에 그리스도께서 우리를 위하여 죽으심으로 하나님께서 우리에 대한 자기의 사랑을 확증하셨습니다(롬 5:8).

- 독생자라는 말의 의미 - 유일무이한 아들
- 주셨다는 말의 의미 - 아낌없이 내어주심  
- 이 사랑의 동기 - 세상을 사랑하심`,

      '본론 2: 믿는 자에게 주시는 영생': `# 본론 2: 믿는 자에게 주시는 영생

하나님의 사랑은 단순한 감정이 아니라 구체적인 행동으로 나타났습니다. 그 결과가 바로 믿는 자에게 주어지는 영생입니다.

영생은 단순히 죽지 않는 것이 아니라, 하나님과의 올바른 관계 속에서 누리는 참된 생명입니다.

*"영생은 곧 유일하신 참 하나님과 그가 보내신 자 예수 그리스도를 아는 것이니이다"* (요 17:3)`
    };

    return mockContent[part] || `# ${part}

이 부분의 내용을 작성해주세요. AI가 생성한 초안을 바탕으로 수정하고 보완할 수 있습니다.

관련 성경 구절과 주석을 참고하여 내용을 풍성하게 만들어보세요.`;
  };



  useEffect(() => {
    // 각 목차 부분에 대한 빈 내용 초기화
    const initialContent: { [key: string]: string } = {};
    outline.parts.forEach(part => {
      initialContent[part] = '';
    });
    setSermonContent(initialContent);
  }, [outline]);

  const generateSermonPart = async (part: string) => {
    setIsGenerating(true);
    setCurrentEditingPart(part);
    setError(null);
    
    try {
      // 설정 로드
      const savedSettings = localStorage.getItem('appSettings');
      if (savedSettings) {
        const settings: AppSettings = JSON.parse(savedSettings);
        
        // AI 서비스 사용해서 설교문 부분 생성
        const aiService = getAIService(settings.ai);
        const verseText = `${selectedVerse.book} ${selectedVerse.chapter}:${selectedVerse.verse} - ${selectedVerse.text}`;
        const generatedContent = await aiService.generateSermonPart(
          verseText, 
          selectedTopic, 
          part,
          `전체 목차: ${outline.parts.join(', ')}`
        );
        
        setSermonContent(prev => ({
          ...prev,
          [part]: generatedContent
        }));
      } else {
        throw new Error('AI 설정이 없습니다. 설정을 먼저 구성해주세요.');
      }
    } catch (error) {
      console.error('AI 설교문 생성 실패:', error);
      setError(error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.');
      
      // AI 실패 시 기본 내용 사용
      const generatedContent = generateMockSermon(part);
      setSermonContent(prev => ({
        ...prev,
        [part]: generatedContent
      }));
    } finally {
      setIsGenerating(false);
      setCurrentEditingPart('');
    }
  };

  const generateAllParts = async () => {
    for (const part of outline.parts) {
      await generateSermonPart(part);
    }
  };

  const updateSermonPart = (part: string, content: string) => {
    setSermonContent(prev => ({
      ...prev,
      [part]: content
    }));
  };

  const generateImage = async (part: string) => {
    setIsGeneratingImage(true);
    setCurrentImagePart(part);
    setError(null);
    
    try {
      // 설정 로드
      const savedSettings = localStorage.getItem('appSettings');
      if (savedSettings) {
        const settings: AppSettings = JSON.parse(savedSettings);
        
        // AI 서비스 사용해서 이미지 프롬프트 생성
        const aiService = getAIService(settings.ai);
        const verseText = `${selectedVerse.book} ${selectedVerse.chapter}:${selectedVerse.verse} - ${selectedVerse.text}`;
        const imagePrompt = await aiService.generateImagePrompt(verseText, selectedTopic, part);
        
        // 실제 이미지 생성 (여기서는 Placeholder 이미지 사용)
        // 실제 구현 시에는 DALL-E, Midjourney, Stable Diffusion 등의 API 사용
        const imageUrl = `https://picsum.photos/800/600?random=${Date.now()}`;
        
        setGeneratedImages(prev => ({
          ...prev,
          [part]: imageUrl
        }));
        
        // 생성된 프롬프트를 로컬 스토리지에 저장
        const imagePrompts = JSON.parse(localStorage.getItem('imagePrompts') || '{}');
        imagePrompts[part] = imagePrompt;
        localStorage.setItem('imagePrompts', JSON.stringify(imagePrompts));
        
      } else {
        throw new Error('AI 설정이 없습니다. 설정을 먼저 구성해주세요.');
      }
    } catch (error) {
      console.error('이미지 생성 실패:', error);
      setError(error instanceof Error ? error.message : '이미지 생성 중 오류가 발생했습니다.');
    } finally {
      setIsGeneratingImage(false);
      setCurrentImagePart('');
    }
  };

  const viewImage = (part: string) => {
    const imageUrl = generatedImages[part];
    if (imageUrl) {
      setCurrentViewingImage(imageUrl);
      setShowImageModal(true);
    }
  };

  const downloadImage = async (imageUrl: string) => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sermon-image-${Date.now()}.jpg`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('이미지 다운로드 실패:', error);
      alert('이미지 다운로드에 실패했습니다.');
    }
  };

  const saveSermon = async () => {
    const verseText = `${selectedVerse.book} ${selectedVerse.chapter}:${selectedVerse.verse}`;
    const fullSermon = {
      verse: verseText,
      topic: selectedTopic,
      outline: outline.parts,
      content: sermonContent,
      createdAt: new Date().toISOString()
    };

    // localStorage에 저장
    const savedSermons = JSON.parse(localStorage.getItem('savedSermons') || '[]');
    savedSermons.push(fullSermon);
    localStorage.setItem('savedSermons', JSON.stringify(savedSermons));

    alert('설교문이 저장되었습니다!');
  };

  const exportToWord = () => {
    // 간단한 텍스트 내보내기 (실제로는 더 복잡한 Word 문서 생성 필요)
    const fullText = outline.parts.map(part => 
      `${part}\n\n${sermonContent[part] || ''}\n\n`
    ).join('---\n\n');
    
    alert('Word 내보내기 기능은 개발 중입니다.\n\n현재는 텍스트 복사만 가능합니다:\n\n' + fullText);
  };



  return (
    <div className="max-w-7xl mx-auto">
      <div className={`rounded-xl shadow-lg p-8 ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
        {/* 헤더 */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              ✍️ 설교문 작성
            </h2>
            <p className={`mt-1 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              본문: <span className={`font-semibold ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>
                {selectedVerse.book} {selectedVerse.chapter}:{selectedVerse.verse}
              </span>
            </p>
            <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              주제: <span className={`font-semibold ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>{selectedTopic}</span>
            </p>
          </div>
        </div>

        {/* AI 오류 알림 */}
        {error && (
          <div className={`mb-4 p-4 border rounded-lg ${
            darkMode 
              ? 'bg-yellow-900/20 border-yellow-800' 
              : 'bg-yellow-50 border-yellow-200'
          }`}>
            <div className="flex items-center">
              <span className={`mr-2 ${darkMode ? 'text-yellow-400' : 'text-yellow-600'}`}>⚠️</span>
              <div>
                <p className={`text-sm font-medium ${darkMode ? 'text-yellow-200' : 'text-yellow-800'}`}>
                  AI 설교문 생성 실패
                </p>
                <p className={`text-xs mt-1 ${darkMode ? 'text-yellow-300' : 'text-yellow-700'}`}>
                  {error} 기본 템플릿을 사용합니다.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* 액션 버튼들 */}
        <div className="mb-6 flex flex-wrap gap-3">
          <button
            onClick={generateAllParts}
            disabled={isGenerating}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              isGenerating
                ? darkMode
                  ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {isGenerating ? '🤖 생성 중...' : '🤖 전체 AI 생성'}
          </button>
          

          
          <button
            onClick={saveSermon}
            className={`px-4 py-2 border rounded-lg font-medium transition-colors ${
              darkMode
                ? 'border-gray-600 text-gray-300 hover:bg-gray-700'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            💾 저장
          </button>
          
          <button
            onClick={exportToWord}
            className={`px-4 py-2 border rounded-lg font-medium transition-colors ${
              darkMode
                ? 'border-gray-600 text-gray-300 hover:bg-gray-700'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            📄 Word 내보내기
          </button>
        </div>

        <div className="grid grid-cols-1 gap-6">
          {/* 메인 에디터 영역 */}
          <div className="space-y-6">
            {outline.parts.map((part, index) => (
              <div key={index} className={`border rounded-lg p-4 ${
                darkMode ? 'border-gray-600' : 'border-gray-200'
              }`}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                    {part}
                  </h3>
                  <div className="flex gap-2">
                    <button
                      onClick={() => generateSermonPart(part)}
                      disabled={isGenerating}
                      className={`px-3 py-1 text-sm rounded transition-colors ${
                        isGenerating && currentEditingPart === part
                          ? darkMode
                            ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                          : 'bg-blue-600 hover:bg-blue-700 text-white'
                      }`}
                    >
                      {isGenerating && currentEditingPart === part ? '생성 중...' : '🤖 AI 생성'}
                    </button>
                    
                    <button
                      onClick={() => generateImage(part)}
                      disabled={isGeneratingImage}
                      className={`px-3 py-1 text-sm rounded transition-colors ${
                        isGeneratingImage && currentImagePart === part
                          ? darkMode
                            ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                          : 'bg-purple-600 hover:bg-purple-700 text-white'
                      }`}
                    >
                      {isGeneratingImage && currentImagePart === part ? '생성 중...' : '🎨 이미지 생성'}
                    </button>
                    
                    {generatedImages[part] && (
                      <button
                        onClick={() => viewImage(part)}
                        className="px-3 py-1 text-sm rounded bg-green-600 hover:bg-green-700 text-white transition-colors"
                      >
                        🖼️ 이미지 보기
                      </button>
                    )}
                  </div>
                </div>
                
                <SimpleEditor
                  value={sermonContent[part] || ''}
                  onChange={(value) => updateSermonPart(part, value)}
                  placeholder={`${part}에 대한 내용을 작성하거나 AI 생성 버튼을 클릭하세요...`}
                  minHeight="300px"
                  darkMode={darkMode}
                />
              </div>
            ))}
          </div>


        </div>

        {/* 이미지 모달 */}
        {showImageModal && currentViewingImage && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className={`max-w-4xl max-h-[90vh] p-6 rounded-lg ${
              darkMode ? 'bg-gray-800' : 'bg-white'
            }`}>
              <div className="flex justify-between items-center mb-4">
                <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                  생성된 이미지
                </h3>
                <button
                  onClick={() => setShowImageModal(false)}
                  className={`text-2xl ${darkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'}`}
                >
                  ×
                </button>
              </div>
              
              <div className="mb-4">
                <img
                  src={currentViewingImage}
                  alt="생성된 설교 이미지"
                  className="max-w-full max-h-[60vh] object-contain rounded-lg"
                />
              </div>
              
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => downloadImage(currentViewingImage)}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  💾 다운로드
                </button>
                <button
                  onClick={() => setShowImageModal(false)}
                  className={`px-4 py-2 border rounded-lg transition-colors ${
                    darkMode
                      ? 'border-gray-600 text-gray-300 hover:bg-gray-700'
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  닫기
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SermonEditor; 