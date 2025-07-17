import { AISettings } from '../../types/global';

export interface AIRequest {
  prompt: string;
  context?: string;
  maxTokens?: number;
  temperature?: number;
}

export interface AIResponse {
  content: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
}

class AIService {
  private settings: AISettings;

  constructor(settings: AISettings) {
    this.settings = settings;
  }

  updateSettings(settings: AISettings) {
    this.settings = settings;
  }

  async generateContent(request: AIRequest): Promise<AIResponse> {
    // 시스템 프롬프트를 데이터베이스에서 가져오기
    const systemPrompt = await this.getStoredPrompt('system-prompt');
    const updatedSettings = { ...this.settings, systemPrompt };
    
    switch (this.settings.provider) {
      case 'google':
        return this.callGoogleAI(request, updatedSettings);
      case 'openai':
        return this.callOpenAI(request, updatedSettings);
      case 'anthropic':
        return this.callAnthropic(request);
      case 'local':
        return this.callLocalAI(request);
      default:
        throw new Error(`지원하지 않는 AI 제공업체: ${this.settings.provider}`);
    }
  }

  private async callGoogleAI(request: AIRequest, settings?: AISettings): Promise<AIResponse> {
    const currentSettings = settings || this.settings;
    
    if (!currentSettings.apiKey) {
      throw new Error('Google AI Studio API 키가 필요합니다.');
    }

    const url = `https://generativelanguage.googleapis.com/v1beta/models/${currentSettings.model}:generateContent?key=${currentSettings.apiKey}`;
    
    const payload = {
      contents: [
        {
          parts: [
            {
              text: `${currentSettings.systemPrompt}\n\n${request.context ? `컨텍스트: ${request.context}\n\n` : ''}요청: ${request.prompt}`
            }
          ]
        }
      ],
      generationConfig: {
        temperature: request.temperature || currentSettings.temperature,
        maxOutputTokens: request.maxTokens || currentSettings.maxTokens,
        topP: 0.8,
        topK: 10
      }
    };

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Google AI API 오류: ${errorData.error?.message || response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.candidates || data.candidates.length === 0) {
        throw new Error('Google AI에서 응답을 생성하지 못했습니다.');
      }

      const content = data.candidates[0].content.parts[0].text;
      
      return {
        content,
        usage: {
          promptTokens: data.usageMetadata?.promptTokenCount || 0,
          completionTokens: data.usageMetadata?.candidatesTokenCount || 0,
          totalTokens: data.usageMetadata?.totalTokenCount || 0
        }
      };
    } catch (error) {
      console.error('Google AI API 호출 실패:', error);
      throw error;
    }
  }

  private async callOpenAI(request: AIRequest, settings?: AISettings): Promise<AIResponse> {
    const currentSettings = settings || this.settings;
    
    if (!currentSettings.apiKey) {
      throw new Error('OpenAI API 키가 필요합니다.');
    }

    const url = 'https://api.openai.com/v1/chat/completions';
    
    const payload = {
      model: currentSettings.model,
      messages: [
        {
          role: 'system',
          content: currentSettings.systemPrompt
        },
        {
          role: 'user',
          content: `${request.context ? `컨텍스트: ${request.context}\n\n` : ''}${request.prompt}`
        }
      ],
      temperature: request.temperature || currentSettings.temperature,
      max_tokens: request.maxTokens || currentSettings.maxTokens
    };

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.settings.apiKey}`
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`OpenAI API 오류: ${errorData.error?.message || response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.choices || data.choices.length === 0) {
        throw new Error('OpenAI에서 응답을 생성하지 못했습니다.');
      }

      const content = data.choices[0].message.content;
      
      return {
        content,
        usage: {
          promptTokens: data.usage?.prompt_tokens || 0,
          completionTokens: data.usage?.completion_tokens || 0,
          totalTokens: data.usage?.total_tokens || 0
        }
      };
    } catch (error) {
      console.error('OpenAI API 호출 실패:', error);
      throw error;
    }
  }

  private async callAnthropic(request: AIRequest): Promise<AIResponse> {
    if (!this.settings.apiKey) {
      throw new Error('Anthropic API 키가 필요합니다.');
    }

    const url = 'https://api.anthropic.com/v1/messages';
    
    const payload = {
      model: this.settings.model,
      max_tokens: request.maxTokens || this.settings.maxTokens,
      temperature: request.temperature || this.settings.temperature,
      system: this.settings.systemPrompt,
      messages: [
        {
          role: 'user',
          content: `${request.context ? `컨텍스트: ${request.context}\n\n` : ''}${request.prompt}`
        }
      ]
    };

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': this.settings.apiKey,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Anthropic API 오류: ${errorData.error?.message || response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.content || data.content.length === 0) {
        throw new Error('Anthropic에서 응답을 생성하지 못했습니다.');
      }

      const content = data.content[0].text;
      
      return {
        content,
        usage: {
          promptTokens: data.usage?.input_tokens || 0,
          completionTokens: data.usage?.output_tokens || 0,
          totalTokens: (data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0)
        }
      };
    } catch (error) {
      console.error('Anthropic API 호출 실패:', error);
      throw error;
    }
  }

  private async callLocalAI(request: AIRequest): Promise<AIResponse> {
    const url = `${this.settings.baseUrl || 'http://localhost:11434'}/api/generate`;
    
    const payload = {
      model: this.settings.model,
      prompt: `${this.settings.systemPrompt}\n\n${request.context ? `컨텍스트: ${request.context}\n\n` : ''}요청: ${request.prompt}`,
      stream: false,
      options: {
        temperature: request.temperature || this.settings.temperature,
        num_predict: request.maxTokens || this.settings.maxTokens
      }
    };

    console.log('Ollama 요청 URL:', url);
    console.log('Ollama 요청 페이로드:', JSON.stringify(payload, null, 2));

    try {
      // 먼저 Ollama 서버가 실행 중인지 확인
      const healthCheck = await fetch(`${this.settings.baseUrl || 'http://localhost:11434'}/api/tags`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      }).catch(() => null);

      if (!healthCheck || !healthCheck.ok) {
        throw new Error('Ollama 서버에 연결할 수 없습니다. Ollama가 실행 중인지 확인해주세요.');
      }

      console.log('Ollama 서버 연결 확인됨');

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      console.log('Ollama 응답 상태:', response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Ollama 오류 응답:', errorText);
        throw new Error(`로컬 AI 오류 (${response.status}): ${response.statusText}\n상세: ${errorText}`);
      }

      const data = await response.json();
      console.log('Ollama 응답 데이터:', data);
      
      if (!data.response) {
        console.error('Ollama 응답에 response 필드가 없음:', data);
        throw new Error('로컬 AI에서 응답을 생성하지 못했습니다.');
      }

      console.log('Ollama 생성된 응답:', data.response);

      return {
        content: data.response,
        usage: {
          promptTokens: 0,
          completionTokens: 0,
          totalTokens: 0
        }
      };
    } catch (error) {
      console.error('로컬 AI API 호출 실패:', error);
      
      // 더 구체적인 에러 메시지 제공
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Ollama 서버에 연결할 수 없습니다. http://localhost:11434에서 Ollama가 실행 중인지 확인해주세요.');
      }
      
      throw error;
    }
  }

  async testConnection(): Promise<boolean> {
    try {
      const testRequest: AIRequest = {
        prompt: '안녕하세요. 연결 테스트입니다. 간단히 "연결 성공"이라고 답해주세요.',
        maxTokens: 50,
        temperature: 0.1
      };

      const response = await this.generateContent(testRequest);
      return response.content.length > 0;
    } catch (error) {
      console.error('AI 연결 테스트 실패:', error);
      return false;
    }
  }

  // 저장된 프롬프트 가져오기
  private async getStoredPrompt(promptId: string): Promise<string> {
    try {
      const prompt = await window.electronAPI.getPrompt(promptId);
      if (prompt) {
        return prompt.content;
      }
    } catch (error) {
      console.error('저장된 프롬프트 로드 실패:', error);
    }
    
    // 기본 프롬프트 반환
    return this.getDefaultPrompt(promptId);
  }

  private getDefaultPrompt(promptId: string): string {
    // 하드코딩된 프롬프트 제거 - 모든 프롬프트는 DB에서 관리
    console.warn(`프롬프트 '${promptId}'를 DB에서 찾을 수 없습니다. 개발자 도구에서 프롬프트를 확인하세요.`);
    return `프롬프트 '${promptId}'를 찾을 수 없습니다. 개발자 도구에서 프롬프트를 설정하세요.`;
  }

  // 설교문 관련 특화 메서드들
  async generateTopics(verse: string): Promise<string[]> {
    const promptTemplate = await this.getStoredPrompt('topic-generation');
    const prompt = promptTemplate.replace('{verse}', verse);
    
    const request: AIRequest = {
      prompt,
      maxTokens: 300
    };

    try {
      const response = await this.generateContent(request);
      return this.parseTopicsFromResponse(response.content);
    } catch (error) {
      console.error('주제 생성 실패:', error);
      throw error;
    }
  }

  async generateOutline(verse: string, topic: string): Promise<string[]> {
    const promptTemplate = await this.getStoredPrompt('outline-generation');
    const prompt = promptTemplate.replace('{verse}', verse).replace('{topic}', topic);
    
    const request: AIRequest = {
      prompt,
      maxTokens: 300
    };

    try {
      const response = await this.generateContent(request);
      return this.parseOutlineFromResponse(response.content);
    } catch (error) {
      console.error('목차 생성 실패:', error);
      throw error;
    }
  }

  async generateSermonPart(verse: string, topic: string, part: string, context?: string): Promise<string> {
    const promptTemplate = await this.getStoredPrompt('sermon-part-generation');
    const prompt = promptTemplate
      .replace('{verse}', verse)
      .replace('{topic}', topic)
      .replace('{part}', part)
      .replace('{context ? `추가 컨텍스트: ${context}` : \'\'}', context ? `추가 컨텍스트: ${context}` : '');
    
    const request: AIRequest = {
      prompt,
      maxTokens: 1500
    };

    try {
      const response = await this.generateContent(request);
      return response.content;
    } catch (error) {
      console.error('설교문 부분 생성 실패:', error);
      throw error;
    }
  }

  async generateImagePrompt(verse: string, topic: string, part: string): Promise<string> {
    const promptTemplate = await this.getStoredPrompt('image-prompt-generation');
    const prompt = promptTemplate
      .replace('{verse}', verse)
      .replace('{topic}', topic)
      .replace('{part}', part);
    
    const request: AIRequest = {
      prompt,
      maxTokens: 200
    };

    try {
      const response = await this.generateContent(request);
      return response.content.trim();
    } catch (error) {
      console.error('이미지 프롬프트 생성 실패:', error);
      throw error;
    }
  }

  private parseTopicsFromResponse(response: string): string[] {
    console.log('주제 파싱 시작, 원본 응답:', response);
    
    const topics: string[] = [];
    
    // 1단계: TOPIC1:, TOPIC2: 형식 찾기 (가장 우선)
    const topicPattern = /TOPIC\d+:\s*(.+?)$/gm;
    const topicMatches = [...response.matchAll(topicPattern)];
    
    if (topicMatches.length > 0) {
      console.log('TOPIC 패턴 매치:', topicMatches);
      for (const match of topicMatches) {
        const topic = match[1].trim();
        if (topic && topic.length > 3 && topic.length < 100) {
          topics.push(topic);
        }
      }
      
      if (topics.length > 0) {
        console.log('TOPIC 패턴으로 파싱된 주제들:', topics);
        return topics.slice(0, 5);
      }
    }

    // 2단계: 숫자. 주제명 형식 찾기
    const numberedPattern = /^(\d+)\.\s*(.+?)$/gm;
    const numberedMatches = [...response.matchAll(numberedPattern)];
    
    if (numberedMatches.length > 0) {
      console.log('숫자 패턴 매치:', numberedMatches);
      for (const match of numberedMatches) {
        const topic = match[2].trim();
        // 설명이 아닌 주제만 추출 (너무 긴 텍스트 제외)
        if (topic && topic.length > 3 && topic.length < 100 && !topic.includes('본문은') && !topic.includes('설교 주제')) {
          topics.push(topic);
        }
      }
      
      if (topics.length > 0) {
        console.log('숫자 패턴으로 파싱된 주제들:', topics);
        return topics.slice(0, 5);
      }
    }

    // 3단계: **주제명** 형식 찾기 (주제만, 설명 제외)
    const boldPattern = /\*\*([^*]+?)\*\*/g;
    const boldMatches = [...response.matchAll(boldPattern)];
    
    if (boldMatches.length > 0) {
      console.log('볼드 패턴 매치:', boldMatches);
      for (const match of boldMatches) {
        const topic = match[1].trim();
        // 주제로 보이는 텍스트만 추출 (숫자로 시작하고 적절한 길이)
        if (topic && 
            topic.length > 5 && 
            topic.length < 80 && 
            topic.match(/^\d+\./) &&
            !topic.includes('본문은') && 
            !topic.includes('설교 주제') &&
            !topic.includes('예시') &&
            !topic.includes('사진') &&
            !topic.includes('강조된')) {
          // 숫자와 점 제거
          const cleanTopic = topic.replace(/^\d+\.\s*/, '').replace(/:$/, '').trim();
          if (cleanTopic) {
            topics.push(cleanTopic);
          }
        }
      }
      
      if (topics.length > 0) {
        console.log('볼드 패턴으로 파싱된 주제들:', topics);
        return topics.slice(0, 5);
      }
    }

    // 4단계: 실패한 경우 빈 배열 반환
    console.log('모든 패턴 매치 실패, 빈 배열 반환');
    return [];
  }

  private parseOutlineFromResponse(response: string): string[] {
    console.log('목차 파싱 시작, 원본 응답:', response);
    
    const outline: string[] = [];
    
    // 1단계: **숫자. 제목:** 형식 찾기 (마크다운 볼드)
    const boldNumberPattern = /\*\*(\d+\.\s*[^*:]+)(?:[:*]|\*\*)/g;
    const boldMatches = [...response.matchAll(boldNumberPattern)];
    
    if (boldMatches.length > 0) {
      console.log('볼드 숫자 패턴 매치:', boldMatches);
      for (const match of boldMatches) {
        const title = match[1].trim();
        if (title && title.includes('서론') || title.includes('본론') || title.includes('결론')) {
          outline.push(title);
        }
      }
      
      if (outline.length > 0) {
        console.log('볼드 패턴으로 파싱된 목차:', outline);
        return outline;
      }
    }

    // 2단계: 일반 숫자. 제목 형식 찾기
    const lines = response.split('\n').filter(line => line.trim());
    
    for (const line of lines) {
      // 숫자. 형식 매치
      const numberMatch = line.match(/^\*?\*?(\d+\.\s*[^*]+?)(?:\*\*?)?$/);
      if (numberMatch) {
        let title = numberMatch[1].trim();
        // 마크다운 기호 제거
        title = title.replace(/\*\*/g, '').replace(/\*/g, '').replace(/:$/, '').trim();
        
        if (title && (title.includes('서론') || title.includes('본론') || title.includes('결론'))) {
          outline.push(title);
        }
      }
    }
    
    // 3단계: 서론, 본론, 결론이 포함된 라인 직접 찾기
    if (outline.length === 0) {
      for (const line of lines) {
        const cleanLine = line.replace(/\*\*/g, '').replace(/\*/g, '').replace(/^#+\s*/, '').trim();
        
        if (cleanLine.match(/^\d+\.\s*(서론|본론|결론)/)) {
          outline.push(cleanLine);
        }
      }
    }
    
    console.log('최종 파싱된 목차:', outline);
    return outline;
  }
}

// 싱글톤 인스턴스
let aiServiceInstance: AIService | null = null;

export const getAIService = (settings?: AISettings): AIService => {
  if (!aiServiceInstance && settings) {
    aiServiceInstance = new AIService(settings);
  } else if (aiServiceInstance && settings) {
    aiServiceInstance.updateSettings(settings);
  }
  
  if (!aiServiceInstance) {
    throw new Error('AI 서비스가 초기화되지 않았습니다. 설정을 먼저 로드해주세요.');
  }
  
  return aiServiceInstance;
};

export default AIService; 