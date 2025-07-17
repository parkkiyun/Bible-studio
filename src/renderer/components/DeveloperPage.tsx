import React, { useState, useEffect } from 'react';
import PromptManager from './PromptManager';
import '../styles/DeveloperPage.css';

interface Version {
  version: string;
  verse_count: number;
  sample_book: string;
  sample_text: string;
}

interface VersionStats {
  book_name: string;
  verse_count: number;
  min_chapter: number;
  max_chapter: number;
}

interface DatabaseInfo {
  table_name: string;
  total_rows: number;
  version_count: number;
  book_count: number;
}

interface VersionDisplayName {
  version_id: string;
  display_name: string;
  created_at?: string;
  updated_at?: string;
}

interface DeveloperPageProps {
  darkMode: boolean;
}

const DeveloperPage: React.FC<DeveloperPageProps> = ({ darkMode }) => {
  const [activeTab, setActiveTab] = useState<'database' | 'prompts'>('database');
  const [versions, setVersions] = useState<Version[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<string>('');
  const [versionStats, setVersionStats] = useState<VersionStats[]>([]);
  const [databaseInfo, setDatabaseInfo] = useState<DatabaseInfo[]>([]);
  const [displayNames, setDisplayNames] = useState<VersionDisplayName[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  
  // 새 번역본 추가 상태
  const [newVersionId, setNewVersionId] = useState('');
  const [newVersionName, setNewVersionName] = useState('');
  const [importData, setImportData] = useState('');
  
  // 번역본 이름 변경 상태
  const [editingVersion, setEditingVersion] = useState<string>('');
  const [newName, setNewName] = useState('');
  
  // 표시이름 관리 상태
  const [editingDisplayName, setEditingDisplayName] = useState<string>('');
  const [newDisplayName, setNewDisplayName] = useState('');

  useEffect(() => {
    loadVersions();
    loadDatabaseInfo();
    loadDisplayNames();
  }, []);

  const loadVersions = async () => {
    try {
      setLoading(true);
      const data = await window.electronAPI.getVersions();
      setVersions(data);
    } catch (error) {
      setMessage(`번역본 로드 실패: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const loadDisplayNames = async () => {
    try {
      const data = await window.electronAPI.getVersionDisplayNames();
      setDisplayNames(data);
    } catch (error) {
      setMessage(`표시이름 로드 실패: ${error}`);
    }
  };

  const loadDatabaseInfo = async () => {
    try {
      const data = await window.electronAPI.getDatabaseInfo();
      setDatabaseInfo(data);
    } catch (error) {
      setMessage(`데이터베이스 정보 로드 실패: ${error}`);
    }
  };

  const loadVersionStats = async (versionId: string) => {
    try {
      setLoading(true);
      const data = await window.electronAPI.getVersionStats(versionId);
      setVersionStats(data);
      setSelectedVersion(versionId);
    } catch (error) {
      setMessage(`번역본 통계 로드 실패: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const deleteVersion = async (versionId: string) => {
    if (!confirm(`'${versionId}' 번역본을 정말 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.`)) {
      return;
    }

    try {
      setLoading(true);
      const success = await window.electronAPI.deleteVersion(versionId);
      if (success) {
        setMessage(`'${versionId}' 번역본이 삭제되었습니다.`);
        loadVersions();
        loadDatabaseInfo();
        if (selectedVersion === versionId) {
          setSelectedVersion('');
          setVersionStats([]);
        }
      } else {
        setMessage(`'${versionId}' 번역본 삭제에 실패했습니다.`);
      }
    } catch (error) {
      setMessage(`삭제 중 오류 발생: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const updateVersionName = async (oldVersionId: string, newVersionId: string) => {
    try {
      setLoading(true);
      const success = await window.electronAPI.updateVersionName(oldVersionId, newVersionId);
      if (success) {
        setMessage(`번역본 이름이 '${oldVersionId}'에서 '${newVersionId}'로 변경되었습니다.`);
        loadVersions();
        setEditingVersion('');
        setNewName('');
        if (selectedVersion === oldVersionId) {
          setSelectedVersion(newVersionId);
        }
      } else {
        setMessage(`번역본 이름 변경에 실패했습니다.`);
      }
    } catch (error) {
      setMessage(`이름 변경 중 오류 발생: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const addVersion = async () => {
    if (!newVersionId || !importData) {
      setMessage('번역본 ID와 데이터를 모두 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      
      // JSON 형식으로 데이터 파싱
      const verses = JSON.parse(importData);
      
      const versionData = {
        versionId: newVersionId,
        verses: verses
      };

      const success = await window.electronAPI.addVersion(versionData);
      if (success) {
        setMessage(`'${newVersionId}' 번역본이 추가되었습니다.`);
        loadVersions();
        loadDatabaseInfo();
        setNewVersionId('');
        setNewVersionName('');
        setImportData('');
      } else {
        setMessage(`번역본 추가에 실패했습니다.`);
      }
    } catch (error) {
      setMessage(`번역본 추가 중 오류 발생: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const clearMessage = () => {
    setMessage('');
  };

  const getDisplayName = (versionId: string) => {
    const displayName = displayNames.find(d => d.version_id === versionId);
    if (displayName) return displayName.display_name;
    
    const defaultNames: { [key: string]: string } = {
      'korean-standard': '개역한글',
      'korean-revised': '한글킹제임스성경',
      'korean-traditional': '개역한글',
      'korean-contemporary': '현대인의성경',
      'korean-new-standard': '표준새번역',
      'korean-new-translation': '새번역',
      'korean-new-revised': '개역개정',
      'niv': 'NIV'
    };
    
    return defaultNames[versionId] || versionId;
  };

  const setVersionDisplayName = async (versionId: string, displayName: string) => {
    try {
      setLoading(true);
      const success = await window.electronAPI.setVersionDisplayName(versionId, displayName);
      if (success) {
        setMessage(`'${versionId}'의 표시 이름이 '${displayName}'으로 설정되었습니다.`);
        loadDisplayNames();
        setEditingDisplayName('');
        setNewDisplayName('');
      } else {
        setMessage(`표시 이름 설정에 실패했습니다.`);
      }
    } catch (error) {
      setMessage(`표시 이름 설정 중 오류 발생: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const removeVersionDisplayName = async (versionId: string) => {
    try {
      setLoading(true);
      const success = await window.electronAPI.removeVersionDisplayName(versionId);
      if (success) {
        setMessage(`'${versionId}'의 표시 이름이 기본값으로 재설정되었습니다.`);
        loadDisplayNames();
      } else {
        setMessage(`표시 이름 제거에 실패했습니다.`);
      }
    } catch (error) {
      setMessage(`표시 이름 제거 중 오류 발생: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number) => {
    return num.toLocaleString();
  };

  const themeClasses = {
    container: darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-900',
    tab: darkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-900',
    activeTab: darkMode ? 'bg-blue-600 text-white' : 'bg-blue-500 text-white',
    inactiveTab: darkMode ? 'bg-gray-700 hover:bg-gray-600 text-gray-300' : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
  };

  return (
    <div className={`developer-page ${themeClasses.container}`}>
      <div className="developer-header">
        <h1>🛠️ 개발자 도구</h1>
        <p>데이터베이스 번역본 관리 및 프롬프트 편집</p>
      </div>

      {/* 탭 네비게이션 */}
      <div className="flex border-b mb-6">
        <button
          onClick={() => setActiveTab('database')}
          className={`px-6 py-3 font-medium rounded-t-lg transition-colors ${
            activeTab === 'database' ? themeClasses.activeTab : themeClasses.inactiveTab
          }`}
        >
          📊 데이터베이스 관리
        </button>
        <button
          onClick={() => setActiveTab('prompts')}
          className={`px-6 py-3 font-medium rounded-t-lg transition-colors ${
            activeTab === 'prompts' ? themeClasses.activeTab : themeClasses.inactiveTab
          }`}
        >
          🤖 프롬프트 관리
        </button>
      </div>

      {message && (
        <div className="message-box">
          <span>{message}</span>
          <button onClick={clearMessage}>×</button>
        </div>
      )}

      {loading && <div className="loading">처리 중...</div>}

      {/* 탭 콘텐츠 */}
      {activeTab === 'database' ? (
        <div>
          {/* 데이터베이스 정보 */}
      <section className="db-info-section">
        <h2>📊 데이터베이스 정보</h2>
        <div className="db-info-grid">
          {databaseInfo.map((info, index) => (
            <div key={index} className="db-info-card">
              <h3>{info.table_name}</h3>
              <div className="stat">
                <span>총 행 수:</span>
                <span>{formatNumber(info.total_rows)}</span>
              </div>
              {info.version_count > 0 && (
                <div className="stat">
                  <span>번역본 수:</span>
                  <span>{info.version_count}</span>
                </div>
              )}
              <div className="stat">
                <span>책 수:</span>
                <span>{info.book_count}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 번역본 목록 */}
      <section className="versions-section">
        <h2>📚 번역본 목록</h2>
        <div className="versions-grid">
          {versions.map((version) => (
            <div key={version.version} className="version-card">
              <div className="version-header">
                <div className="version-title">
                  <h3>{version.version}</h3>
                  <div className="display-name">
                    성경 뷰어 표시: <strong>{getDisplayName(version.version)}</strong>
                  </div>
                </div>
                <div className="version-actions">
                  <button 
                    onClick={() => loadVersionStats(version.version)}
                    disabled={loading}
                  >
                    통계
                  </button>
                  <button 
                    onClick={() => {
                      setEditingDisplayName(version.version);
                      setNewDisplayName(getDisplayName(version.version));
                    }}
                    disabled={loading}
                  >
                    표시이름 변경
                  </button>
                  <button 
                    onClick={() => {
                      setEditingVersion(version.version);
                      setNewName(version.version);
                    }}
                    disabled={loading}
                  >
                    ID변경
                  </button>
                  <button 
                    onClick={() => deleteVersion(version.version)}
                    disabled={loading}
                    className="delete-btn"
                  >
                    삭제
                  </button>
                </div>
              </div>
              <div className="version-info">
                <div className="stat">
                  <span>구절 수:</span>
                  <span>{formatNumber(version.verse_count)}</span>
                </div>
                <div className="sample-text">
                  <strong>{version.sample_book}:</strong>
                  <span>{version.sample_text?.substring(0, 50)}...</span>
                </div>
              </div>
              
              {editingDisplayName === version.version && (
                <div className="edit-form">
                  <label>성경 뷰어에 표시될 이름:</label>
                  <input
                    type="text"
                    value={newDisplayName}
                    onChange={(e) => setNewDisplayName(e.target.value)}
                    placeholder="예: 개역개정판, 새번역성경 등"
                  />
                  <div className="edit-actions">
                    <button 
                      onClick={() => setVersionDisplayName(version.version, newDisplayName)}
                      disabled={loading || !newDisplayName}
                    >
                      저장
                    </button>
                    <button 
                      onClick={() => removeVersionDisplayName(version.version)}
                      disabled={loading}
                      className="reset-btn"
                    >
                      기본값으로
                    </button>
                    <button 
                      onClick={() => {
                        setEditingDisplayName('');
                        setNewDisplayName('');
                      }}
                    >
                      취소
                    </button>
                  </div>
                </div>
              )}

              {editingVersion === version.version && (
                <div className="edit-form">
                  <label>번역본 ID 변경:</label>
                  <input
                    type="text"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder="새 번역본 ID"
                  />
                  <div className="edit-actions">
                    <button 
                      onClick={() => updateVersionName(version.version, newName)}
                      disabled={loading || !newName || newName === version.version}
                    >
                      저장
                    </button>
                    <button 
                      onClick={() => {
                        setEditingVersion('');
                        setNewName('');
                      }}
                    >
                      취소
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* 번역본 통계 */}
      {selectedVersion && versionStats.length > 0 && (
        <section className="stats-section">
          <h2>📈 '{selectedVersion}' 번역본 통계</h2>
          <div className="stats-grid">
            {versionStats.map((stat, index) => (
              <div key={index} className="stat-card">
                <h4>{stat.book_name}</h4>
                <div className="stat">
                  <span>구절 수:</span>
                  <span>{formatNumber(stat.verse_count)}</span>
                </div>
                <div className="stat">
                  <span>장 범위:</span>
                  <span>{stat.min_chapter} - {stat.max_chapter}</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 새 번역본 추가 */}
      <section className="add-version-section">
        <h2>➕ 새 번역본 추가</h2>
        <div className="add-form">
          <div className="form-group">
            <label>번역본 ID:</label>
            <input
              type="text"
              value={newVersionId}
              onChange={(e) => setNewVersionId(e.target.value)}
              placeholder="예: korean-new-version"
            />
          </div>
          
          <div className="form-group">
            <label>데이터 (JSON 형식):</label>
            <textarea
              value={importData}
              onChange={(e) => setImportData(e.target.value)}
              placeholder={`[
  {
    "book_name": "창세기",
    "chapter": 1,
    "verse": 1,
    "text": "태초에 하나님이 천지를 창조하시니라",
    "book_code": 1
  },
  ...
]`}
              rows={10}
            />
          </div>
          
          <button 
            onClick={addVersion}
            disabled={loading || !newVersionId || !importData}
            className="add-btn"
          >
            번역본 추가
          </button>
        </div>
      </section>
        </div>
      ) : (
        <div className="h-full">
          <PromptManager darkMode={darkMode} />
        </div>
      )}
    </div>
  );
};

export default DeveloperPage; 