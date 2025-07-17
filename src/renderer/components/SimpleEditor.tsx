import React, { useState, useRef, useEffect } from 'react';

interface SimpleEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  darkMode?: boolean;
  className?: string;
}

const SimpleEditor: React.FC<SimpleEditorProps> = ({
  value,
  onChange,
  placeholder = "내용을 입력하세요...",
  darkMode = false,
  className = ""
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isFormatting, setIsFormatting] = useState(false);

  const themeClasses = {
    container: darkMode 
      ? 'bg-gray-800 border-gray-600' 
      : 'bg-white border-gray-300',
    textarea: darkMode 
      ? 'bg-gray-800 text-white placeholder-gray-400' 
      : 'bg-white text-gray-900 placeholder-gray-500',
    toolbar: darkMode 
      ? 'bg-gray-700 border-gray-600' 
      : 'bg-gray-50 border-gray-200',
    button: darkMode 
      ? 'text-gray-300 hover:text-white hover:bg-gray-600' 
      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
  };

  // 자동 높이 조절
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = textarea.scrollHeight + 'px';
    }
  }, [value]);

  const insertText = (before: string, after: string = '') => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = value.substring(start, end);
    
    const newText = value.substring(0, start) + 
                   before + selectedText + after + 
                   value.substring(end);
    
    onChange(newText);
    
    // 커서 위치 조정
    setTimeout(() => {
      textarea.focus();
      const newCursorPos = start + before.length + selectedText.length;
      textarea.setSelectionRange(newCursorPos, newCursorPos);
    }, 0);
  };

  const formatButtons = [
    { label: 'B', action: () => insertText('**', '**'), title: '굵게' },
    { label: 'I', action: () => insertText('*', '*'), title: '기울임' },
    { label: 'H1', action: () => insertText('# '), title: '제목 1' },
    { label: 'H2', action: () => insertText('## '), title: '제목 2' },
    { label: 'H3', action: () => insertText('### '), title: '제목 3' },
    { label: '•', action: () => insertText('- '), title: '목록' },
    { label: '1.', action: () => insertText('1. '), title: '번호 목록' },
    { label: '"', action: () => insertText('> '), title: '인용' },
  ];

  return (
    <div className={`border rounded-lg overflow-hidden ${themeClasses.container} ${className}`}>
      {/* 툴바 */}
      <div className={`flex items-center px-3 py-2 border-b ${themeClasses.toolbar}`}>
        <div className="flex items-center space-x-1">
          {formatButtons.map((button, index) => (
            <button
              key={index}
              onClick={button.action}
              className={`px-2 py-1 text-xs font-medium rounded transition-colors ${themeClasses.button}`}
              title={button.title}
              type="button"
            >
              {button.label}
            </button>
          ))}
        </div>
        <div className="ml-auto text-xs text-gray-500">
          마크다운 지원
        </div>
      </div>

      {/* 텍스트 에리어 */}
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={`w-full min-h-[200px] p-4 resize-none outline-none ${themeClasses.textarea}`}
        style={{ minHeight: '200px' }}
      />
    </div>
  );
};

export default SimpleEditor; 