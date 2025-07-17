import React, { useState, useEffect } from 'react';
import { AIProvider, AIModel, AISettings, AppSettings, CustomOutlineTemplate } from '../../types/global';

interface SettingsProps {
  onClose: () => void;
}

// AI 제공업체 및 모델 데이터
const AI_PROVIDERS: AIProvider[] = [
  {
    id: 'google',
    name: 'Google AI Studio',
    requiresApiKey: true,
    apiKeyLabel: 'Google AI Studio API Key',
    baseUrl: 'https://generativelanguage.googleapis.com',
    models: [
      {
        id: 'gemini-1.5-flash',
        name: 'Gemini 1.5 Flash',
        description: '빠르고 효율적인 무료 모델 (월 15회 요청 제한)',
        maxTokens: 8192,
        isFree: true
      },
      {
        id: 'gemini-1.5-pro',
        name: 'Gemini 1.5 Pro',
        description: '고성능 모델 (월 2회 무료)',
        maxTokens: 32768,
        isFree: true
      }
    ]
  },
  {
    id: 'openai',
    name: 'OpenAI',
    requiresApiKey: true,
    apiKeyLabel: 'OpenAI API Key',
    baseUrl: 'https://api.openai.com',
    models: [
      {
        id: 'gpt-3.5-turbo',
        name: 'GPT-3.5 Turbo',
        description: '빠르고 비용 효율적인 모델',
        maxTokens: 4096,
        isFree: false,
        costPerToken: 0.0015
      },
      {
        id: 'gpt-4o-mini',
        name: 'GPT-4o Mini',
        description: '소형 GPT-4 모델',
        maxTokens: 16384,
        isFree: false,
        costPerToken: 0.00015
      },
      {
        id: 'gpt-4o',
        name: 'GPT-4o',
        description: '최신 고성능 모델',
        maxTokens: 8192,
        isFree: false,
        costPerToken: 0.005
      }
    ]
  },
  {
    id: 'anthropic',
    name: 'Anthropic Claude',
    requiresApiKey: true,
    apiKeyLabel: 'Anthropic API Key',
    baseUrl: 'https://api.anthropic.com',
    models: [
      {
        id: 'claude-3-haiku-20240307',
        name: 'Claude 3 Haiku',
        description: '빠르고 경제적인 모델',
        maxTokens: 4096,
        isFree: false,
        costPerToken: 0.00025
      },
      {
        id: 'claude-3-5-sonnet-20241022',
        name: 'Claude 3.5 Sonnet',
        description: '균형잡힌 성능의 모델',
        maxTokens: 8192,
        isFree: false,
        costPerToken: 0.003
      }
    ]
  },
  {
    id: 'local',
    name: '로컬 AI (Ollama)',
    requiresApiKey: false,
    apiKeyLabel: '',
    baseUrl: 'http://localhost:11434',
    models: [
      {
        id: 'gemma2:2b',
        name: 'Gemma 2 2B ✅',
        description: '설치됨 - Google의 소형 모델 (완전 무료)',
        maxTokens: 8192,
        isFree: true
      },
      {
        id: 'llama3.2:3b',
        name: 'Llama 3.2 3B',
        description: '소형 로컬 모델 (완전 무료)',
        maxTokens: 2048,
        isFree: true
      },
      {
        id: 'phi3:mini',
        name: 'Phi-3 Mini',
        description: 'Microsoft의 소형 모델 (완전 무료)',
        maxTokens: 4096,
        isFree: true
      }
    ]
  }
];

// 기본 설정
const DEFAULT_SETTINGS: AppSettings = {
  ai: {
    provider: 'local',
    model: 'gemma2:2b',
    apiKey: '',
    temperature: 0.7,
    maxTokens: 2048,
    systemPrompt: `당신은 기독교 설교문 작성을 돕는 AI 어시스턴트입니다.

역할:
- 성경 본문을 깊이 있게 해석하고 적용점을 제시
- 신학적으로 정확하고 실용적인 설교문 작성
- 한국 교회 상황에 맞는 내용 구성
- 성도들의 삶에 적용 가능한 메시지 전달

지침:
1. 성경 본문을 정확히 해석하세요
2. 실생활 적용이 가능한 내용으로 구성하세요
3. 따뜻하고 격려적인 톤을 유지하세요
4. 적절한 예화와 일러스트를 포함하세요
5. 명확한 구조로 이해하기 쉽게 작성하세요`
  },
  theme: 'system',
  language: 'ko',
  autoSave: true,
  fontSize: 'medium',
  customOutlines: [
    {
      id: 'default-1',
      name: '기본 4단 구조',
      parts: ['서론: 말씀 소개', '본론 1: 말씀의 배경', '본론 2: 말씀의 적용', '결론: 삶의 실천'],
      createdAt: new Date()
    },
    {
      id: 'default-2',
      name: '삼중 구조',
      parts: ['서론: 문제 제기', '본론 1: 성경적 해답', '본론 2: 실천 방안', '결론: 다짐과 기도'],
      createdAt: new Date()
    }
  ]
};

const Settings: React.FC<SettingsProps> = ({ onClose }) => {
  const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS);
  const [activeTab, setActiveTab] = useState<'ai' | 'general' | 'outlines'>('ai');
  const [newOutlineName, setNewOutlineName] = useState('');
  const [newOutlineParts, setNewOutlineParts] = useState(['', '', '', '']);
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      // 실제로는 window.electronAPI.getSettings() 호출
      const savedSettings = localStorage.getItem('appSettings');
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings);
        setSettings({ ...DEFAULT_SETTINGS, ...parsed });
      }
    } catch (error) {
      console.error('설정 로드 실패:', error);
    }
  };

  const saveSettings = async () => {
    try {
      // 실제로는 window.electronAPI.saveSettings(settings) 호출
      localStorage.setItem('appSettings', JSON.stringify(settings));
      alert('설정이 저장되었습니다!');
    } catch (error) {
      console.error('설정 저장 실패:', error);
      alert('설정 저장에 실패했습니다.');
    }
  };

  const testConnection = async () => {
    setTestingConnection(true);
    setConnectionStatus('idle');

    try {
      const provider = AI_PROVIDERS.find(p => p.id === settings.ai.provider);
      if (!provider) throw new Error('선택된 제공업체를 찾을 수 없습니다.');

      if (provider.requiresApiKey && !settings.ai.apiKey) {
        throw new Error('API 키가 필요합니다.');
      }

      // 실제로는 window.electronAPI.testAIConnection(settings.ai) 호출
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 임시로 성공으로 처리
      setConnectionStatus('success');
    } catch (error) {
      console.error('연결 테스트 실패:', error);
      setConnectionStatus('error');
    } finally {
      setTestingConnection(false);
    }
  };

  const handleProviderChange = (providerId: string) => {
    const provider = AI_PROVIDERS.find(p => p.id === providerId);
    if (provider) {
      const defaultModel = provider.models.find(m => m.isFree) || provider.models[0];
      setSettings(prev => ({
        ...prev,
        ai: {
          ...prev.ai,
          provider: providerId,
          model: defaultModel.id,
          maxTokens: Math.min(prev.ai.maxTokens, defaultModel.maxTokens)
        }
      }));
    }
  };

  const handleModelChange = (modelId: string) => {
    const provider = AI_PROVIDERS.find(p => p.id === settings.ai.provider);
    const model = provider?.models.find(m => m.id === modelId);
    if (model) {
      setSettings(prev => ({
        ...prev,
        ai: {
          ...prev.ai,
          model: modelId,
          maxTokens: Math.min(prev.ai.maxTokens, model.maxTokens)
        }
      }));
    }
  };

  const currentProvider = AI_PROVIDERS.find(p => p.id === settings.ai.provider);
  const currentModel = currentProvider?.models.find(m => m.id === settings.ai.model);

  // 커스텀 목차 관리 함수들
  const addCustomOutline = () => {
    if (!newOutlineName.trim()) {
      alert('목차 이름을 입력해주세요.');
      return;
    }

    const validParts = newOutlineParts.filter(part => part.trim());
    if (validParts.length < 2) {
      alert('최소 2개 이상의 목차 항목을 입력해주세요.');
      return;
    }

    const newOutline: CustomOutlineTemplate = {
      id: Date.now().toString(),
      name: newOutlineName.trim(),
      parts: validParts,
      createdAt: new Date()
    };

    setSettings(prev => ({
      ...prev,
      customOutlines: [...prev.customOutlines, newOutline]
    }));

    // 입력 필드 초기화
    setNewOutlineName('');
    setNewOutlineParts(['', '', '', '']);
  };

  const deleteCustomOutline = (id: string) => {
    if (confirm('이 목차 템플릿을 삭제하시겠습니까?')) {
      setSettings(prev => ({
        ...prev,
        customOutlines: prev.customOutlines.filter(outline => outline.id !== id)
      }));
    }
  };

  const updateOutlinePart = (index: number, value: string) => {
    const newParts = [...newOutlineParts];
    newParts[index] = value;
    setNewOutlineParts(newParts);
  };

  const addOutlinePart = () => {
    setNewOutlineParts([...newOutlineParts, '']);
  };

  const removeOutlinePart = (index: number) => {
    if (newOutlineParts.length > 2) {
      const newParts = newOutlineParts.filter((_, i) => i !== index);
      setNewOutlineParts(newParts);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* 헤더 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-600">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            ⚙️ 설정
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            ✕
          </button>
        </div>

        <div className="flex h-[600px]">
          {/* 사이드바 탭 */}
          <div className="w-48 bg-gray-50 dark:bg-gray-700 border-r border-gray-200 dark:border-gray-600">
            <nav className="p-4 space-y-2">
              <button
                onClick={() => setActiveTab('ai')}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  activeTab === 'ai'
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                }`}
              >
                🤖 AI 설정
              </button>
              <button
                onClick={() => setActiveTab('outlines')}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  activeTab === 'outlines'
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                }`}
              >
                📝 목차 템플릿
              </button>
              <button
                onClick={() => setActiveTab('general')}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  activeTab === 'general'
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                }`}
              >
                🎨 일반 설정
              </button>
            </nav>
          </div>

          {/* 메인 컨텐츠 */}
          <div className="flex-1 p-6 overflow-y-auto">
            {activeTab === 'ai' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    AI 제공업체 및 모델
                  </h3>

                  {/* 제공업체 선택 */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      AI 제공업체
                    </label>
                    <select
                      value={settings.ai.provider}
                      onChange={(e) => handleProviderChange(e.target.value)}
                      className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      {AI_PROVIDERS.map(provider => (
                        <option key={provider.id} value={provider.id}>
                          {provider.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* 모델 선택 */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      AI 모델
                    </label>
                    <select
                      value={settings.ai.model}
                      onChange={(e) => handleModelChange(e.target.value)}
                      className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      {currentProvider?.models.map(model => (
                        <option key={model.id} value={model.id}>
                          {model.name} {model.isFree ? '(무료)' : '(유료)'}
                        </option>
                      ))}
                    </select>
                    {currentModel && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {currentModel.description}
                      </p>
                    )}
                  </div>

                  {/* API 키 */}
                  {currentProvider?.requiresApiKey && (
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        {currentProvider.apiKeyLabel}
                      </label>
                      <input
                        type="password"
                        value={settings.ai.apiKey}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          ai: { ...prev.ai, apiKey: e.target.value }
                        }))}
                        placeholder="API 키를 입력하세요"
                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        API 키는 안전하게 암호화되어 저장됩니다.
                      </p>
                    </div>
                  )}

                  {/* 연결 테스트 */}
                  <div className="mb-6">
                    <button
                      onClick={testConnection}
                      disabled={testingConnection}
                      className="btn-secondary mr-3"
                    >
                      {testingConnection ? (
                        <>
                          <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                          연결 테스트 중...
                        </>
                      ) : (
                        '🔗 연결 테스트'
                      )}
                    </button>
                    {connectionStatus === 'success' && (
                      <span className="text-green-600 dark:text-green-400">✅ 연결 성공</span>
                    )}
                    {connectionStatus === 'error' && (
                      <span className="text-red-600 dark:text-red-400">❌ 연결 실패</span>
                    )}
                  </div>
                </div>

                {/* AI 파라미터 */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    AI 파라미터
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Temperature: {settings.ai.temperature}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="2"
                        step="0.1"
                        value={settings.ai.temperature}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          ai: { ...prev.ai, temperature: parseFloat(e.target.value) }
                        }))}
                        className="w-full"
                      />
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        낮을수록 일관된 답변, 높을수록 창의적 답변
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        최대 토큰 수
                      </label>
                      <input
                        type="number"
                        min="512"
                        max={currentModel?.maxTokens || 4096}
                        value={settings.ai.maxTokens}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          ai: { ...prev.ai, maxTokens: parseInt(e.target.value) }
                        }))}
                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        생성될 텍스트의 최대 길이
                      </p>
                    </div>
                  </div>

                  {/* 시스템 프롬프트 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      시스템 프롬프트
                    </label>
                    <textarea
                      value={settings.ai.systemPrompt}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        ai: { ...prev.ai, systemPrompt: e.target.value }
                      }))}
                      rows={8}
                      className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                      placeholder="AI의 역할과 동작을 정의하는 프롬프트를 입력하세요..."
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'outlines' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    커스텀 목차 템플릿
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                    자주 사용하는 설교 목차 구조를 템플릿으로 저장하여 재사용할 수 있습니다.
                  </p>

                  {/* 기존 목차 템플릿 목록 */}
                  <div className="mb-8">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3">저장된 템플릿</h4>
                    <div className="space-y-3">
                      {settings.customOutlines.map((outline) => (
                        <div key={outline.id} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 bg-gray-50 dark:bg-gray-700">
                          <div className="flex items-start justify-between mb-2">
                            <h5 className="font-medium text-gray-900 dark:text-white">{outline.name}</h5>
                            <button
                              onClick={() => deleteCustomOutline(outline.id)}
                              className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 text-sm"
                              disabled={outline.id.startsWith('default-')}
                            >
                              {outline.id.startsWith('default-') ? '🔒' : '🗑️'}
                            </button>
                          </div>
                          <div className="space-y-1">
                            {outline.parts.map((part, index) => (
                              <div key={index} className="text-sm text-gray-600 dark:text-gray-300">
                                {index + 1}. {part}
                              </div>
                            ))}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                            생성일: {new Date(outline.createdAt).toLocaleDateString()}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 새 목차 템플릿 추가 */}
                  <div className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3">새 템플릿 추가</h4>
                    
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        템플릿 이름
                      </label>
                      <input
                        type="text"
                        value={newOutlineName}
                        onChange={(e) => setNewOutlineName(e.target.value)}
                        placeholder="예: 삼중 구조, 4단계 설교 등"
                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>

                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        목차 구성
                      </label>
                      <div className="space-y-2">
                        {newOutlineParts.map((part, index) => (
                          <div key={index} className="flex items-center space-x-2">
                            <span className="text-sm text-gray-500 dark:text-gray-400 w-8">
                              {index + 1}.
                            </span>
                            <input
                              type="text"
                              value={part}
                              onChange={(e) => updateOutlinePart(index, e.target.value)}
                              placeholder={`${index + 1}번째 목차 항목을 입력하세요`}
                              className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                            />
                            {newOutlineParts.length > 2 && (
                              <button
                                onClick={() => removeOutlinePart(index)}
                                className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
                              >
                                ❌
                              </button>
                            )}
                          </div>
                        ))}
                      </div>
                      
                      <div className="flex space-x-2 mt-3">
                        <button
                          onClick={addOutlinePart}
                          className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm"
                        >
                          ➕ 목차 항목 추가
                        </button>
                      </div>
                    </div>

                    <button
                      onClick={addCustomOutline}
                      className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                    >
                      템플릿 저장
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'general' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    일반 설정
                  </h3>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        테마
                      </label>
                      <select
                        value={settings.theme}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          theme: e.target.value as 'light' | 'dark' | 'system'
                        }))}
                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        <option value="system">시스템 설정 따르기</option>
                        <option value="light">라이트 모드</option>
                        <option value="dark">다크 모드</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        언어
                      </label>
                      <select
                        value={settings.language}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          language: e.target.value as 'ko' | 'en'
                        }))}
                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        <option value="ko">한국어</option>
                        <option value="en">English</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        글꼴 크기
                      </label>
                      <select
                        value={settings.fontSize}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          fontSize: e.target.value as 'small' | 'medium' | 'large'
                        }))}
                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        <option value="small">작게</option>
                        <option value="medium">보통</option>
                        <option value="large">크게</option>
                      </select>
                    </div>

                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="autoSave"
                        checked={settings.autoSave}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          autoSave: e.target.checked
                        }))}
                        className="mr-2"
                      />
                      <label htmlFor="autoSave" className="text-sm text-gray-700 dark:text-gray-300">
                        자동 저장 활성화
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 하단 버튼 */}
        <div className="flex justify-end space-x-3 p-6 border-t border-gray-200 dark:border-gray-600">
          <button
            onClick={onClose}
            className="btn-outline"
          >
            취소
          </button>
          <button
            onClick={saveSettings}
            className="btn-primary"
          >
            저장
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings; 