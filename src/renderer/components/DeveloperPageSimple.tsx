import React, { useState, useEffect } from 'react';
import '../styles/DeveloperPage.css';

interface Version {
  version: string;
  verse_count: number;
  sample_book: string;
  sample_text: string;
}

interface VersionDisplayName {
  version_id: string;
  display_name: string;
}

const DeveloperPageSimple: React.FC = () => {
  const [versions, setVersions] = useState<Version[]>([]);
  const [displayNames, setDisplayNames] = useState<VersionDisplayName[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [editingDisplayName, setEditingDisplayName] = useState<string>('');
  const [newDisplayName, setNewDisplayName] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [versionsData, displayNamesData] = await Promise.all([
        window.electronAPI.getVersions(),
        window.electronAPI.getVersionDisplayNames()
      ]);
      setVersions(versionsData);
      setDisplayNames(displayNamesData);
    } catch (error) {
      setMessage(`데이터 로드 실패: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const getDisplayName = (versionId: string) => {
    const displayName = displayNames.find(d => d.version_id === versionId);
    if (displayName) return displayName.display_name;
    
    const defaultNames: { [key: string]: string } = {
      'korean-standard': '새번역',
      'korean-revised': '개역개정',
      'korean-traditional': '개역한글판',
      'korean-contemporary': '현대인의성경',
      'korean-new-standard': '표준새번역',
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
        loadData();
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
        loadData();
      } else {
        setMessage(`표시 이름 제거에 실패했습니다.`);
      }
    } catch (error) {
      setMessage(`표시 이름 제거 중 오류 발생: ${error}`);
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
        loadData();
      } else {
        setMessage(`'${versionId}' 번역본 삭제에 실패했습니다.`);
      }
    } catch (error) {
      setMessage(`삭제 중 오류 발생: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="developer-page">
      <div className="developer-header">
        <h1>🛠️ 개발자 도구</h1>
        <p>번역본 관리 및 표시 이름 설정</p>
      </div>

      {message && (
        <div className="message-box">
          <span>{message}</span>
          <button onClick={() => setMessage('')}>×</button>
        </div>
      )}

      {loading && <div className="loading">처리 중...</div>}

      <section className="versions-section">
        <h2>📚 번역본 목록 및 표시 이름 관리</h2>
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
                    onClick={() => {
                      setEditingDisplayName(version.version);
                      setNewDisplayName(getDisplayName(version.version));
                    }}
                    disabled={loading}
                  >
                    표시이름 변경
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
                  <span>{version.verse_count.toLocaleString()}</span>
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
            </div>
          ))}
        </div>
      </section>

      <section className="info-section">
        <h2>💡 사용 안내</h2>
        <div className="info-card">
          <h3>표시 이름 관리</h3>
          <ul>
            <li><strong>표시이름 변경</strong>: 성경 뷰어의 번역본 선택 메뉴에 표시될 이름을 설정합니다</li>
            <li><strong>기본값으로</strong>: 사용자 지정 표시 이름을 제거하고 기본 이름으로 되돌립니다</li>
            <li><strong>삭제</strong>: 번역본 전체를 데이터베이스에서 완전히 제거합니다</li>
          </ul>
          
          <h3>현재 기본 표시 이름</h3>
          <ul>
            <li>korean-standard → 새번역</li>
            <li>korean-revised → 개역개정</li>
            <li>korean-traditional → 개역한글판</li>
            <li>korean-contemporary → 현대인의성경</li>
            <li>korean-new-standard → 표준새번역</li>
            <li>niv → NIV</li>
          </ul>
        </div>
      </section>
    </div>
  );
};

export default DeveloperPageSimple; 