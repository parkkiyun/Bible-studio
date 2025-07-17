import React, { useState, useEffect } from 'react';
import { Book, Verse, Commentary } from '../../types/global';
import { bibleService } from '../services/bibleService';

interface BibleViewerProps {
  onVerseSelect?: (verse: { book: string; chapter: number; verse: number; text: string }) => void;
  darkMode: boolean;
}

const BibleViewer: React.FC<BibleViewerProps> = ({ onVerseSelect, darkMode }) => {
  const [books, setBooks] = useState<Book[]>([]);
  const [verses, setVerses] = useState<Verse[]>([]);
  const [commentaries, setCommentaries] = useState<Commentary[]>([]);
  const [comparisonVerses, setComparisonVerses] = useState<Verse[]>([]);
  const [versions, setVersions] = useState<{ id: string; name: string }[]>([]);
  const [selectedBook, setSelectedBook] = useState<string>('요한복음');
  const [selectedChapter, setSelectedChapter] = useState<number>(3);
  const [selectedVersion, setSelectedVersion] = useState<string>('korean-contemporary');
  const [comparisonVersion, setComparisonVersion] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [showBookModal, setShowBookModal] = useState<boolean>(false);
  const [selectedVerses, setSelectedVerses] = useState<Set<number>>(new Set());
  const [showCommentary, setShowCommentary] = useState<boolean>(true);
  const [lastClickedVerse, setLastClickedVerse] = useState<number | null>(null);

  const loadVersions = async () => {
    try {
      const availableVersions = await bibleService.getAvailableVersions();
      setVersions(availableVersions);
    } catch (error) {
      console.error('번역본 목록 로드 실패:', error);
      setVersions([]);
    }
  };

  useEffect(() => {
    const initializeViewer = async () => {
      await loadBooks();
      await loadVersions();
      // 초기 데이터가 설정된 후 구절 로딩
      await loadVerses();
      await loadCommentaries();
    };
    initializeViewer();
  }, []);

  useEffect(() => {
    if (selectedBook && selectedChapter) {
      loadVerses();
      loadCommentaries();
    }
  }, [selectedBook, selectedChapter, selectedVersion]);

  useEffect(() => {
    if (comparisonVersion && selectedBook && selectedChapter) {
      loadComparisonVerses();
    } else {
      setComparisonVerses([]);
    }
  }, [comparisonVersion, selectedBook, selectedChapter]);

  const loadBooks = async () => {
    try {
      const booksData = await bibleService.getBooks();
      setBooks(booksData);
    } catch (error) {
      console.error('성경 책 로드 실패:', error);
    }
  };

  const loadVerses = async () => {
    if (!selectedBook || !selectedChapter) return;

    setLoading(true);
    try {
      const versesData = await bibleService.getVerses(selectedBook, selectedChapter, selectedVersion);
      setVerses(versesData);
    } catch (error) {
      console.error('구절 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadComparisonVerses = async () => {
    if (!selectedBook || !selectedChapter || !comparisonVersion) return;

    try {
      const versesData = await bibleService.getVerses(selectedBook, selectedChapter, comparisonVersion);
      setComparisonVerses(versesData);
    } catch (error) {
      console.error('비교 구절 로드 실패:', error);
    }
  };

  const loadCommentaries = async () => {
    if (!selectedBook || !selectedChapter) return;

    try {
      const commentariesData = await bibleService.getCommentaries(selectedBook, selectedChapter);
      setCommentaries(commentariesData);
    } catch (error) {
      console.error('주석 로드 실패:', error);
    }
  };

  const handleBookSelect = (bookName: string) => {
    setSelectedBook(bookName);
    setSelectedChapter(1);
    setShowBookModal(false);
    setSelectedVerses(new Set());
  };

  const handleChapterSelect = (chapter: number) => {
    setSelectedChapter(chapter);
    setSelectedVerses(new Set());
  };

  const handleVerseClick = (verseNumber: number, event: React.MouseEvent) => {
    if (event.ctrlKey || event.metaKey) {
      // Ctrl/Cmd + 클릭: 다중 선택
      const newSelected = new Set(selectedVerses);
      if (newSelected.has(verseNumber)) {
        newSelected.delete(verseNumber);
      } else {
        newSelected.add(verseNumber);
      }
      setSelectedVerses(newSelected);
    } else if (event.shiftKey && lastClickedVerse !== null) {
      // Shift + 클릭: 범위 선택
      const start = Math.min(lastClickedVerse, verseNumber);
      const end = Math.max(lastClickedVerse, verseNumber);
      const newSelected = new Set(selectedVerses);
      for (let i = start; i <= end; i++) {
        newSelected.add(i);
      }
      setSelectedVerses(newSelected);
    } else {
      // 일반 클릭: 단일 선택
      setSelectedVerses(new Set([verseNumber]));
    }
    setLastClickedVerse(verseNumber);
  };

  const copySelectedVerses = () => {
    if (selectedVerses.size === 0) return;

    const sortedVerses = Array.from(selectedVerses).sort((a, b) => a - b);
    const selectedTexts = sortedVerses.map(verseNum => {
      const verse = verses.find(v => v.verse === verseNum);
      const comparison = comparisonVerses.find(v => v.verse === verseNum);
      
      let text = `${selectedBook} ${selectedChapter}:${verseNum} `;
      if (verse) {
        const versionName = versions.find(v => v.id === selectedVersion)?.name || selectedVersion;
        text += `[${versionName}] ${verse.text}`;
      }
      if (comparison) {
        const compVersionName = versions.find(v => v.id === comparisonVersion)?.name || comparisonVersion;
        text += `\n[${compVersionName}] ${comparison.text}`;
      }
      return text;
    }).join('\n\n');

    navigator.clipboard.writeText(selectedTexts).then(() => {
      alert(`${selectedVerses.size}개 구절이 복사되었습니다.`);
    }).catch(err => {
      console.error('복사 실패:', err);
      alert('복사에 실패했습니다.');
    });
  };

  const handleAIGenerate = () => {
    if (selectedVerses.size === 0 || !onVerseSelect) return;

    const sortedVerses = Array.from(selectedVerses).sort((a, b) => a - b);
    const firstVerse = sortedVerses[0];
    const lastVerse = sortedVerses[sortedVerses.length - 1];
    
    // 선택된 구절들의 텍스트를 합치기
    const selectedTexts = sortedVerses.map(verseNum => {
      const verse = verses.find(v => v.verse === verseNum);
      return verse ? verse.text : '';
    }).filter(text => text).join(' ');

    // AI 도우미로 전달할 구절 정보 생성
    const verseInfo = {
      book: selectedBook,
      chapter: selectedChapter,
      verse: firstVerse,
      text: selectedTexts
    };

    onVerseSelect(verseInfo);
  };

  const getSelectedBook = () => {
    return books.find(book => book.korean_name === selectedBook);
  };

  const getChapterNumbers = () => {
    const book = getSelectedBook();
    if (!book) return [];
    return Array.from({ length: book.chapters }, (_, i) => i + 1);
  };

  const oldTestamentBooks = books.filter(book => book.testament === '구약');
  const newTestamentBooks = books.filter(book => book.testament === '신약');

  const getVerseTitle = (verse: Verse) => {
    // verse_title이 있으면 표시, 없으면 빈 문자열
    return (verse as any).verse_title || '';
  };

  const themeClasses = {
    container: darkMode 
      ? 'bg-gray-900 text-white' 
      : 'bg-white text-gray-900',
    header: darkMode 
      ? 'bg-gradient-to-r from-blue-800 to-blue-900' 
      : 'bg-gradient-to-r from-blue-600 to-blue-800',
    button: darkMode 
      ? 'bg-gray-700 hover:bg-gray-600 text-white border-gray-600' 
      : 'bg-white hover:bg-gray-50 text-gray-700 border-gray-300',
    select: darkMode 
      ? 'bg-gray-700 border-gray-600 text-white' 
      : 'bg-white border-gray-300 text-gray-900',
    modal: darkMode 
      ? 'bg-gray-800 border-gray-700' 
      : 'bg-white border-gray-200',
    verse: darkMode 
      ? 'hover:bg-gray-700 border-gray-700' 
      : 'hover:bg-gray-50 border-gray-200',
    verseSelected: darkMode 
      ? 'bg-blue-800 border-blue-600' 
      : 'bg-blue-100 border-blue-300',
    commentary: darkMode 
      ? 'bg-yellow-900 border-yellow-700 text-yellow-100' 
      : 'bg-yellow-50 border-yellow-300 text-yellow-800'
  };

  return (
    <div className={`flex flex-col h-full ${themeClasses.container}`}>
      {/* 헤더 */}
      <div className={`${themeClasses.header} text-white p-4 shadow-lg`}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">성경 뷰어</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setShowCommentary(!showCommentary)}
              className={`px-3 py-1 rounded text-sm ${themeClasses.button}`}
            >
              {showCommentary ? '주석 숨기기' : '주석 보기'}
            </button>
            {selectedVerses.size > 0 && (
              <div className="flex gap-2">
                <button
                  onClick={copySelectedVerses}
                  className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-sm"
                >
                  복사 ({selectedVerses.size})
                </button>
                <button
                  onClick={handleAIGenerate}
                  className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm"
                >
                  AI 생성 본문 선택
                </button>
              </div>
            )}
          </div>
        </div>

        {/* 번역본 선택 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">번역본</label>
            <select
              value={selectedVersion}
              onChange={(e) => setSelectedVersion(e.target.value)}
              className={`w-full px-3 py-2 rounded border ${themeClasses.select}`}
            >
                          {versions.map(version => (
              <option key={`main-${version.id}`} value={version.id}>
                {version.name}
              </option>
            ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">비교 번역본 (선택사항)</label>
            <select
              value={comparisonVersion}
              onChange={(e) => setComparisonVersion(e.target.value)}
              className={`w-full px-3 py-2 rounded border ${themeClasses.select}`}
            >
              <option value="">선택 안함</option>
              {versions.filter(v => v.id !== selectedVersion).map(version => (
                <option key={`comp-${version.id}`} value={version.id}>
                  {version.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 책/장 선택 */}
        <div className="flex gap-4">
          <button
            onClick={() => setShowBookModal(true)}
            className={`px-4 py-2 rounded border ${themeClasses.button}`}
          >
            {selectedBook}
          </button>
          <select
            value={selectedChapter}
            onChange={(e) => handleChapterSelect(Number(e.target.value))}
            className={`px-3 py-2 rounded border ${themeClasses.select}`}
          >
            {getChapterNumbers().map(num => (
              <option key={`chapter-${num}`} value={num}>{num}장</option>
            ))}
          </select>
        </div>
      </div>

      {/* 본문 영역 */}
      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="text-center py-8">
            <div className="text-lg">로딩 중...</div>
          </div>
        ) : comparisonVersion ? (
          /* 2열 비교 레이아웃 */
          <div className="flex gap-4 h-full">
            {/* 왼쪽 열: 주 번역본 */}
            <div className="flex-1 space-y-3">
              <div className={`sticky top-0 ${themeClasses.container} py-2 border-b mb-4`}>
                <h3 className={`font-semibold text-lg ${darkMode ? 'text-blue-300' : 'text-blue-600'}`}>
                  {versions.find(v => v.id === selectedVersion)?.name || selectedVersion}
                </h3>
              </div>
              {verses.map((verse) => {
                const isSelected = selectedVerses.has(verse.verse);
                const verseTitle = getVerseTitle(verse);
                const commentary = commentaries.find(c => c.verse_start === verse.verse);

                return (
                  <div key={`main-verse-${verse.id || verse.verse}`} className="space-y-2">
                    {/* 구절 제목 (있는 경우) */}
                    {verseTitle && (
                      <div className={`text-sm font-semibold ${darkMode ? 'text-blue-300' : 'text-blue-600'} border-b pb-1`}>
                        {verseTitle}
                      </div>
                    )}
                    
                    {/* 주 번역본 구절 */}
                    <div
                      className={`p-3 rounded border cursor-pointer transition-colors select-none ${
                        isSelected ? themeClasses.verseSelected : themeClasses.verse
                      }`}
                      onClick={(e) => handleVerseClick(verse.verse, e)}
                    >
                      <div className="flex items-start gap-3">
                        <span className={`font-bold text-sm ${darkMode ? 'text-blue-300' : 'text-blue-600'} min-w-[2rem]`}>
                          {verse.verse}
                        </span>
                        <span className="flex-1 leading-relaxed">{verse.text}</span>
                      </div>
                    </div>

                    {/* 주석 (주 번역본 쪽에만 표시) */}
                    {showCommentary && commentary && (
                      <div className={`p-3 rounded border-l-4 ${themeClasses.commentary}`}>
                        <div className="text-sm">
                          <strong>{commentary.author}:</strong> {commentary.content}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* 오른쪽 열: 비교 번역본 */}
            <div className="flex-1 space-y-3">
              <div className={`sticky top-0 ${themeClasses.container} py-2 border-b mb-4`}>
                <h3 className={`font-semibold text-lg ${darkMode ? 'text-green-300' : 'text-green-600'}`}>
                  {versions.find(v => v.id === comparisonVersion)?.name || comparisonVersion}
                </h3>
              </div>
              {comparisonVerses.map((verse) => {
                const isSelected = selectedVerses.has(verse.verse);

                return (
                  <div key={`comp-verse-${verse.id || verse.verse}`} className="space-y-2">
                    {/* 구절 제목 공간 유지 (비교 번역본에서는 빈 공간) */}
                    {getVerseTitle(verses.find(v => v.verse === verse.verse) || verse) && (
                      <div className="h-6"></div>
                    )}
                    
                    {/* 비교 번역본 구절 */}
                    <div
                      className={`p-3 rounded border cursor-pointer transition-colors select-none ${
                        isSelected ? themeClasses.verseSelected : themeClasses.verse
                      }`}
                      onClick={(e) => handleVerseClick(verse.verse, e)}
                    >
                      <div className="flex items-start gap-3">
                        <span className={`font-bold text-sm ${darkMode ? 'text-green-300' : 'text-green-600'} min-w-[2rem]`}>
                          {verse.verse}
                        </span>
                        <span className="flex-1 leading-relaxed">{verse.text}</span>
                      </div>
                    </div>

                    {/* 주석 공간 유지 (비교 번역본에서는 빈 공간) */}
                    {showCommentary && commentaries.find(c => 
                      verse.verse >= c.verse_start && verse.verse <= c.verse_end
                    ) && (
                      <div className="h-16"></div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          /* 단일 번역본 레이아웃 */
          <div className="space-y-3">
            {verses.map((verse) => {
              const isSelected = selectedVerses.has(verse.verse);
              const verseTitle = getVerseTitle(verse);
              const commentary = commentaries.find(c => 
                verse.verse >= c.verse_start && verse.verse <= c.verse_end
              );

              return (
                <div key={`single-verse-${verse.id || verse.verse}`} className="space-y-2">
                  {/* 구절 제목 (있는 경우) */}
                  {verseTitle && (
                    <div className={`text-sm font-semibold ${darkMode ? 'text-blue-300' : 'text-blue-600'} border-b pb-1`}>
                      {verseTitle}
                    </div>
                  )}
                  
                  {/* 구절 */}
                  <div
                    className={`p-3 rounded border cursor-pointer transition-colors select-none ${
                      isSelected ? themeClasses.verseSelected : themeClasses.verse
                    }`}
                    onClick={(e) => handleVerseClick(verse.verse, e)}
                  >
                    <div className="flex items-start gap-3">
                      <span className={`font-bold text-sm ${darkMode ? 'text-blue-300' : 'text-blue-600'} min-w-[2rem]`}>
                        {verse.verse}
                      </span>
                      <span className="flex-1 leading-relaxed">{verse.text}</span>
                    </div>
                  </div>

                  {/* 주석 */}
                  {showCommentary && commentary && (
                    <div className={`p-3 rounded border-l-4 ${themeClasses.commentary}`}>
                      <div className="text-sm">
                        <strong>{commentary.author}:</strong> {commentary.content}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 성경책 선택 모달 */}
      {showBookModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className={`${themeClasses.modal} rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden mx-4`}>
            <div className={`${themeClasses.header} text-white p-4`}>
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold">성경책 선택</h3>
                <button
                  onClick={() => setShowBookModal(false)}
                  className="text-white hover:text-gray-300"
                >
                  ✕
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* 구약 */}
                <div>
                  <h4 className={`text-lg font-bold mb-3 ${darkMode ? 'text-blue-300' : 'text-blue-600'}`}>
                    구약 ({oldTestamentBooks.length}권)
                  </h4>
                  <div className="grid grid-cols-2 gap-2">
                    {oldTestamentBooks.map((book, index) => (
                      <button
                        key={`ot-${book.id || book.book_order || index}`}
                        onClick={() => handleBookSelect(book.korean_name)}
                        className={`p-2 text-left rounded border text-sm ${themeClasses.button}`}
                      >
                        <div className="font-medium">{book.korean_name}</div>
                        <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                          {book.chapters}장
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* 신약 */}
                <div>
                  <h4 className={`text-lg font-bold mb-3 ${darkMode ? 'text-green-300' : 'text-green-600'}`}>
                    신약 ({newTestamentBooks.length}권)
                  </h4>
                  <div className="grid grid-cols-2 gap-2">
                    {newTestamentBooks.map((book, index) => (
                      <button
                        key={`nt-${book.id || book.book_order || index}`}
                        onClick={() => handleBookSelect(book.korean_name)}
                        className={`p-2 text-left rounded border text-sm ${themeClasses.button}`}
                      >
                        <div className="font-medium">{book.korean_name}</div>
                        <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                          {book.chapters}장
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 사용법 안내 */}
      {selectedVerses.size === 0 && (
        <div className={`p-3 text-xs ${darkMode ? 'text-gray-400 bg-gray-800' : 'text-gray-500 bg-gray-50'} border-t`}>
          💡 사용법: 클릭(단일 선택) | Ctrl+클릭(다중 선택) | Shift+클릭(범위 선택) | 선택 후 복사 버튼 클릭
        </div>
      )}
    </div>
  );
};

export default BibleViewer; 