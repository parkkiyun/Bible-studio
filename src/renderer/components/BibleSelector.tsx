import React, { useState, useEffect } from 'react';
import { bibleService } from '../services/bibleService';
import { Book, Verse } from '../../types/global';

interface BibleSelectorProps {
  onVerseSelect: (verse: { book: string; chapter: number; verse: number; text: string }) => void;
  darkMode: boolean;
}

const BibleSelector: React.FC<BibleSelectorProps> = ({ onVerseSelect, darkMode }) => {
  const [books, setBooks] = useState<Book[]>([]);
  const [versions, setVersions] = useState<{ id: string; name: string }[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<string>('korean-standard');
  
  // 시작 구절
  const [startBook, setStartBook] = useState<string>('');
  const [startChapter, setStartChapter] = useState<number>(1);
  const [startVerse, setStartVerse] = useState<number>(1);
  const [startVerses, setStartVerses] = useState<Verse[]>([]);
  
  // 종료 구절
  const [endBook, setEndBook] = useState<string>('');
  const [endChapter, setEndChapter] = useState<number>(1);
  const [endVerse, setEndVerse] = useState<number>(1);
  const [endVerses, setEndVerses] = useState<Verse[]>([]);
  
  const [loading, setLoading] = useState<boolean>(false);
  const [previewText, setPreviewText] = useState<string>('');

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
    select: darkMode 
      ? 'bg-gray-700 border-gray-600 text-white' 
      : 'bg-white border-gray-300 text-gray-900',
    preview: darkMode 
      ? 'bg-gray-700 border-gray-600 text-white' 
      : 'bg-gray-50 border-gray-200 text-gray-800',
    label: darkMode 
      ? 'text-gray-200' 
      : 'text-gray-700'
  };

  // 번역본 목록 로드
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
    loadBooks();
    loadVersions();
  }, []);

  useEffect(() => {
    if (startBook && startChapter) {
      loadStartVerses();
    }
  }, [startBook, startChapter, selectedVersion]);

  useEffect(() => {
    if (endBook && endChapter) {
      loadEndVerses();
    }
  }, [endBook, endChapter, selectedVersion]);

  useEffect(() => {
    generatePreview();
  }, [startBook, startChapter, startVerse, endBook, endChapter, endVerse, startVerses, endVerses]);

  const loadBooks = async () => {
    try {
      const booksData = await bibleService.getBooks();
      setBooks(booksData);
      if (booksData.length > 0) {
        const firstBook = booksData[0].korean_name;
        setStartBook(firstBook);
        setEndBook(firstBook);
      }
    } catch (error) {
      console.error('성경 책 로드 실패:', error);
    }
  };

  const loadStartVerses = async () => {
    if (!startBook || !startChapter) return;
    
    try {
      const versesData = await bibleService.getVerses(startBook, startChapter, selectedVersion);
      setStartVerses(versesData);
      if (versesData.length > 0) {
        setStartVerse(1);
      }
    } catch (error) {
      console.error('시작 구절 로드 실패:', error);
    }
  };

  const loadEndVerses = async () => {
    if (!endBook || !endChapter) return;
    
    try {
      const versesData = await bibleService.getVerses(endBook, endChapter, selectedVersion);
      setEndVerses(versesData);
      if (versesData.length > 0) {
        setEndVerse(1);
      }
    } catch (error) {
      console.error('종료 구절 로드 실패:', error);
    }
  };

  const generatePreview = async () => {
    if (!startBook || !startChapter || !startVerse || !endBook || !endChapter || !endVerse) {
      setPreviewText('');
      return;
    }

    try {
      setLoading(true);
      
      // 시작과 종료가 같은 책인지 확인
      if (startBook === endBook) {
        if (startChapter === endChapter) {
          // 같은 장에서 구절 범위
          const verses = await bibleService.getVerses(startBook, startChapter, selectedVersion);
          const selectedVerses = verses.filter(v => v.verse >= startVerse && v.verse <= endVerse);
          const text = selectedVerses.map(v => v.text).join(' ');
          setPreviewText(text);
        } else {
          // 같은 책, 다른 장
          const allTexts: string[] = [];
          for (let ch = startChapter; ch <= endChapter; ch++) {
            const verses = await bibleService.getVerses(startBook, ch, selectedVersion);
            if (ch === startChapter) {
              // 시작 장: 시작 절부터 끝까지
              const selectedVerses = verses.filter(v => v.verse >= startVerse);
              allTexts.push(...selectedVerses.map(v => v.text));
            } else if (ch === endChapter) {
              // 종료 장: 처음부터 종료 절까지
              const selectedVerses = verses.filter(v => v.verse <= endVerse);
              allTexts.push(...selectedVerses.map(v => v.text));
            } else {
              // 중간 장: 전체
              allTexts.push(...verses.map(v => v.text));
            }
          }
          setPreviewText(allTexts.join(' '));
        }
      } else {
        // 다른 책 (복잡한 경우이므로 기본적으로 시작 구절만 표시)
        const verses = await bibleService.getVerses(startBook, startChapter, selectedVersion);
        const verse = verses.find(v => v.verse === startVerse);
        setPreviewText(verse ? verse.text : '');
      }
    } catch (error) {
      console.error('미리보기 생성 실패:', error);
      setPreviewText('미리보기를 생성할 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleStartBookChange = (bookName: string) => {
    setStartBook(bookName);
    setStartChapter(1);
    setStartVerse(1);
  };

  const handleEndBookChange = (bookName: string) => {
    setEndBook(bookName);
    setEndChapter(1);
    setEndVerse(1);
  };

  const handleStartChapterChange = (chapter: number) => {
    setStartChapter(chapter);
    setStartVerse(1);
  };

  const handleEndChapterChange = (chapter: number) => {
    setEndChapter(chapter);
    setEndVerse(1);
  };

  const getBookChapters = (bookName: string) => {
    const book = books.find(b => b.korean_name === bookName);
    if (!book) return [];
    return Array.from({ length: book.chapters }, (_, i) => i + 1);
  };

  const getStartVerseNumbers = () => {
    return Array.from({ length: startVerses.length }, (_, i) => i + 1);
  };

  const getEndVerseNumbers = () => {
    return Array.from({ length: endVerses.length }, (_, i) => i + 1);
  };

  const handleSubmit = () => {
    if (!previewText) return;

    const verseInfo = {
      book: startBook,
      chapter: startChapter,
      verse: startVerse,
      text: previewText
    };

    onVerseSelect(verseInfo);
  };

  return (
    <div className={`p-6 rounded-lg border shadow-lg ${themeClasses.container}`}>
      <h2 className="text-xl font-bold mb-6">1단계: 성경 구절 선택</h2>
      
      <div className="space-y-6">
        {/* 번역본 선택 */}
        <div>
          <label className={`block text-sm font-medium mb-2 ${themeClasses.label}`}>번역본</label>
          <select
            value={selectedVersion}
            onChange={(e) => setSelectedVersion(e.target.value)}
            className={`w-full px-3 py-2 rounded-lg border ${themeClasses.select}`}
          >
            {versions.map(version => (
              <option key={version.id} value={version.id}>
                {version.name}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 시작 구절 */}
          <div className={`p-4 rounded-lg border ${themeClasses.card}`}>
            <h3 className={`font-semibold mb-4 ${themeClasses.label}`}>시작 구절</h3>
            
            <div className="space-y-3">
              <div>
                <label className={`block text-sm font-medium mb-1 ${themeClasses.label}`}>성경책</label>
                <select
                  value={startBook}
                  onChange={(e) => handleStartBookChange(e.target.value)}
                  className={`w-full px-3 py-2 rounded border ${themeClasses.select}`}
                >
                  <option value="">성경책을 선택하세요</option>
                  {books.map((book, index) => (
                    <option key={`start-book-${book.book_order || index}`} value={book.korean_name}>
                      {book.korean_name}
                    </option>
                  ))}
                </select>
              </div>

              {startBook && (
                <div>
                  <label className={`block text-sm font-medium mb-1 ${themeClasses.label}`}>장</label>
                  <select
                    value={startChapter}
                    onChange={(e) => handleStartChapterChange(Number(e.target.value))}
                    className={`w-full px-3 py-2 rounded border ${themeClasses.select}`}
                  >
                    {getBookChapters(startBook).map((chapter) => (
                      <option key={chapter} value={chapter}>
                        {chapter}장
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {startBook && startChapter && startVerses.length > 0 && (
                <div>
                  <label className={`block text-sm font-medium mb-1 ${themeClasses.label}`}>절</label>
                  <select
                    value={startVerse}
                    onChange={(e) => setStartVerse(Number(e.target.value))}
                    className={`w-full px-3 py-2 rounded border ${themeClasses.select}`}
                  >
                    {getStartVerseNumbers().map((verse) => (
                      <option key={`start-${verse}`} value={verse}>
                        {verse}절
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          </div>

          {/* 종료 구절 */}
          <div className={`p-4 rounded-lg border ${themeClasses.card}`}>
            <h3 className={`font-semibold mb-4 ${themeClasses.label}`}>종료 구절</h3>
            
            <div className="space-y-3">
              <div>
                <label className={`block text-sm font-medium mb-1 ${themeClasses.label}`}>성경책</label>
                <select
                  value={endBook}
                  onChange={(e) => handleEndBookChange(e.target.value)}
                  className={`w-full px-3 py-2 rounded border ${themeClasses.select}`}
                >
                  <option value="">성경책을 선택하세요</option>
                  {books.map((book, index) => (
                    <option key={`end-book-${book.book_order || index}`} value={book.korean_name}>
                      {book.korean_name}
                    </option>
                  ))}
                </select>
              </div>

              {endBook && (
                <div>
                  <label className={`block text-sm font-medium mb-1 ${themeClasses.label}`}>장</label>
                  <select
                    value={endChapter}
                    onChange={(e) => handleEndChapterChange(Number(e.target.value))}
                    className={`w-full px-3 py-2 rounded border ${themeClasses.select}`}
                  >
                    {getBookChapters(endBook).map((chapter) => (
                      <option key={chapter} value={chapter}>
                        {chapter}장
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {endBook && endChapter && endVerses.length > 0 && (
                <div>
                  <label className={`block text-sm font-medium mb-1 ${themeClasses.label}`}>절</label>
                  <select
                    value={endVerse}
                    onChange={(e) => setEndVerse(Number(e.target.value))}
                    className={`w-full px-3 py-2 rounded border ${themeClasses.select}`}
                  >
                    {getEndVerseNumbers().map((verse) => (
                      <option key={`end-${verse}`} value={verse}>
                        {verse}절
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 미리보기 */}
        {previewText && (
          <div className={`p-4 rounded-lg border ${themeClasses.preview}`}>
            <h3 className={`font-semibold mb-2 ${themeClasses.label}`}>
              {startBook} {startChapter}:{startVerse}
              {(startBook !== endBook || startChapter !== endChapter || startVerse !== endVerse) && 
                ` - ${endBook} ${endChapter}:${endVerse}`
              }
            </h3>
            <p className="leading-relaxed">
              {loading ? '로딩 중...' : previewText}
            </p>
          </div>
        )}

        {/* 선택 완료 버튼 */}
        {previewText && !loading && (
          <button
            onClick={handleSubmit}
            className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${themeClasses.button}`}
          >
            이 구절로 설교 준비하기
          </button>
        )}
      </div>
    </div>
  );
};

export default BibleSelector; 