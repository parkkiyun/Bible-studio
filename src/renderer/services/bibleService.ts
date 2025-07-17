// Bible Database Service
// SQLite 데이터베이스와 상호작용하는 서비스

import { Book, Verse, Commentary } from '../../types/global';

// 호환성을 위한 타입 별칭
export type BibleVerse = Verse;
export type BibleBook = Book;

class BibleService {
  private static instance: BibleService;

  private constructor() {}

  static getInstance(): BibleService {
    if (!BibleService.instance) {
      BibleService.instance = new BibleService();
    }
    return BibleService.instance;
  }

  // 모든 성경 책 목록 가져오기
  async getBooks(): Promise<Book[]> {
    try {
      console.log('BibleService: getBooks 호출');
      
      // Electron IPC를 통해 실제 데이터베이스에서 가져오기
      if (window.electronAPI && window.electronAPI.getBibleBooks) {
        console.log('Electron API 사용하여 책 목록 가져오기');
        const books = await window.electronAPI.getBibleBooks();
        console.log('Electron API 응답:', books);
        
        if (books && Array.isArray(books) && books.length > 0) {
          // 데이터베이스 응답을 Book 인터페이스에 맞게 변환
          const convertedBooks: Book[] = books.map((book: any) => ({
            id: book.id,
            korean_name: book.korean_name || book.book_name,
            english_name: book.english_name || book.book_name_english,
            testament: book.testament === 'OT' ? '구약' : book.testament === 'NT' ? '신약' : book.testament,
            chapters: book.chapters || book.total_chapters,
            book_order: book.book_order
          }));
          
          console.log('변환된 책 목록:', convertedBooks.length, '권');
          console.log('첫 번째 책 샘플:', convertedBooks[0]);
          return convertedBooks;
        }
      }
      
      console.log('Electron API 사용 불가 또는 응답 없음, fallback 데이터 사용');
      
      // Fallback: 하드코딩된 데이터 반환
      const books: Book[] = [
        // 구약
        { id: 1, korean_name: '창세기', english_name: 'Genesis', testament: '구약', book_order: 1, chapters: 50 },
        { id: 2, korean_name: '출애굽기', english_name: 'Exodus', testament: '구약', book_order: 2, chapters: 40 },
        { id: 3, korean_name: '레위기', english_name: 'Leviticus', testament: '구약', book_order: 3, chapters: 27 },
        { id: 4, korean_name: '민수기', english_name: 'Numbers', testament: '구약', book_order: 4, chapters: 36 },
        { id: 5, korean_name: '신명기', english_name: 'Deuteronomy', testament: '구약', book_order: 5, chapters: 34 },
        { id: 6, korean_name: '여호수아', english_name: 'Joshua', testament: '구약', book_order: 6, chapters: 24 },
        { id: 7, korean_name: '사사기', english_name: 'Judges', testament: '구약', book_order: 7, chapters: 21 },
        { id: 8, korean_name: '룻기', english_name: 'Ruth', testament: '구약', book_order: 8, chapters: 4 },
        { id: 9, korean_name: '사무엘상', english_name: '1 Samuel', testament: '구약', book_order: 9, chapters: 31 },
        { id: 10, korean_name: '사무엘하', english_name: '2 Samuel', testament: '구약', book_order: 10, chapters: 24 },
        { id: 11, korean_name: '열왕기상', english_name: '1 Kings', testament: '구약', book_order: 11, chapters: 22 },
        { id: 12, korean_name: '열왕기하', english_name: '2 Kings', testament: '구약', book_order: 12, chapters: 25 },
        { id: 13, korean_name: '역대상', english_name: '1 Chronicles', testament: '구약', book_order: 13, chapters: 29 },
        { id: 14, korean_name: '역대하', english_name: '2 Chronicles', testament: '구약', book_order: 14, chapters: 36 },
        { id: 15, korean_name: '에스라', english_name: 'Ezra', testament: '구약', book_order: 15, chapters: 10 },
        { id: 16, korean_name: '느헤미야', english_name: 'Nehemiah', testament: '구약', book_order: 16, chapters: 13 },
        { id: 17, korean_name: '에스더', english_name: 'Esther', testament: '구약', book_order: 17, chapters: 10 },
        { id: 18, korean_name: '욥기', english_name: 'Job', testament: '구약', book_order: 18, chapters: 42 },
        { id: 19, korean_name: '시편', english_name: 'Psalms', testament: '구약', book_order: 19, chapters: 150 },
        { id: 20, korean_name: '잠언', english_name: 'Proverbs', testament: '구약', book_order: 20, chapters: 31 },
        { id: 21, korean_name: '전도서', english_name: 'Ecclesiastes', testament: '구약', book_order: 21, chapters: 12 },
        { id: 22, korean_name: '아가', english_name: 'Song of Songs', testament: '구약', book_order: 22, chapters: 8 },
        { id: 23, korean_name: '이사야', english_name: 'Isaiah', testament: '구약', book_order: 23, chapters: 66 },
        { id: 24, korean_name: '예레미야', english_name: 'Jeremiah', testament: '구약', book_order: 24, chapters: 52 },
        { id: 25, korean_name: '예레미야애가', english_name: 'Lamentations', testament: '구약', book_order: 25, chapters: 5 },
        { id: 26, korean_name: '에스겔', english_name: 'Ezekiel', testament: '구약', book_order: 26, chapters: 48 },
        { id: 27, korean_name: '다니엘', english_name: 'Daniel', testament: '구약', book_order: 27, chapters: 12 },
        { id: 28, korean_name: '호세아', english_name: 'Hosea', testament: '구약', book_order: 28, chapters: 14 },
        { id: 29, korean_name: '요엘', english_name: 'Joel', testament: '구약', book_order: 29, chapters: 3 },
        { id: 30, korean_name: '아모스', english_name: 'Amos', testament: '구약', book_order: 30, chapters: 9 },
        { id: 31, korean_name: '오바댜', english_name: 'Obadiah', testament: '구약', book_order: 31, chapters: 1 },
        { id: 32, korean_name: '요나', english_name: 'Jonah', testament: '구약', book_order: 32, chapters: 4 },
        { id: 33, korean_name: '미가', english_name: 'Micah', testament: '구약', book_order: 33, chapters: 7 },
        { id: 34, korean_name: '나훔', english_name: 'Nahum', testament: '구약', book_order: 34, chapters: 3 },
        { id: 35, korean_name: '하박국', english_name: 'Habakkuk', testament: '구약', book_order: 35, chapters: 3 },
        { id: 36, korean_name: '스바냐', english_name: 'Zephaniah', testament: '구약', book_order: 36, chapters: 3 },
        { id: 37, korean_name: '학개', english_name: 'Haggai', testament: '구약', book_order: 37, chapters: 2 },
        { id: 38, korean_name: '스가랴', english_name: 'Zechariah', testament: '구약', book_order: 38, chapters: 14 },
        { id: 39, korean_name: '말라기', english_name: 'Malachi', testament: '구약', book_order: 39, chapters: 4 },
        
        // 신약
        { id: 40, korean_name: '마태복음', english_name: 'Matthew', testament: '신약', book_order: 40, chapters: 28 },
        { id: 41, korean_name: '마가복음', english_name: 'Mark', testament: '신약', book_order: 41, chapters: 16 },
        { id: 42, korean_name: '누가복음', english_name: 'Luke', testament: '신약', book_order: 42, chapters: 24 },
        { id: 43, korean_name: '요한복음', english_name: 'John', testament: '신약', book_order: 43, chapters: 21 },
        { id: 44, korean_name: '사도행전', english_name: 'Acts', testament: '신약', book_order: 44, chapters: 28 },
        { id: 45, korean_name: '로마서', english_name: 'Romans', testament: '신약', book_order: 45, chapters: 16 },
        { id: 46, korean_name: '고린도전서', english_name: '1 Corinthians', testament: '신약', book_order: 46, chapters: 16 },
        { id: 47, korean_name: '고린도후서', english_name: '2 Corinthians', testament: '신약', book_order: 47, chapters: 13 },
        { id: 48, korean_name: '갈라디아서', english_name: 'Galatians', testament: '신약', book_order: 48, chapters: 6 },
        { id: 49, korean_name: '에베소서', english_name: 'Ephesians', testament: '신약', book_order: 49, chapters: 6 },
        { id: 50, korean_name: '빌립보서', english_name: 'Philippians', testament: '신약', book_order: 50, chapters: 4 },
        { id: 51, korean_name: '골로새서', english_name: 'Colossians', testament: '신약', book_order: 51, chapters: 4 },
        { id: 52, korean_name: '데살로니가전서', english_name: '1 Thessalonians', testament: '신약', book_order: 52, chapters: 5 },
        { id: 53, korean_name: '데살로니가후서', english_name: '2 Thessalonians', testament: '신약', book_order: 53, chapters: 3 },
        { id: 54, korean_name: '디모데전서', english_name: '1 Timothy', testament: '신약', book_order: 54, chapters: 6 },
        { id: 55, korean_name: '디모데후서', english_name: '2 Timothy', testament: '신약', book_order: 55, chapters: 4 },
        { id: 56, korean_name: '디도서', english_name: 'Titus', testament: '신약', book_order: 56, chapters: 3 },
        { id: 57, korean_name: '빌레몬서', english_name: 'Philemon', testament: '신약', book_order: 57, chapters: 1 },
        { id: 58, korean_name: '히브리서', english_name: 'Hebrews', testament: '신약', book_order: 58, chapters: 13 },
        { id: 59, korean_name: '야고보서', english_name: 'James', testament: '신약', book_order: 59, chapters: 5 },
        { id: 60, korean_name: '베드로전서', english_name: '1 Peter', testament: '신약', book_order: 60, chapters: 5 },
        { id: 61, korean_name: '베드로후서', english_name: '2 Peter', testament: '신약', book_order: 61, chapters: 3 },
        { id: 62, korean_name: '요한일서', english_name: '1 John', testament: '신약', book_order: 62, chapters: 5 },
        { id: 63, korean_name: '요한이서', english_name: '2 John', testament: '신약', book_order: 63, chapters: 1 },
        { id: 64, korean_name: '요한삼서', english_name: '3 John', testament: '신약', book_order: 64, chapters: 1 },
        { id: 65, korean_name: '유다서', english_name: 'Jude', testament: '신약', book_order: 65, chapters: 1 },
        { id: 66, korean_name: '요한계시록', english_name: 'Revelation', testament: '신약', book_order: 66, chapters: 22 },
      ];

      return books;
    } catch (error) {
      console.error('성경 책 목록 로드 실패:', error);
      throw new Error('성경 책 목록을 불러올 수 없습니다: ' + (error as Error).message);
    }
  }

  // 특정 장의 구절들 가져오기
  async getVerses(book: string, chapter: number, version: string = 'korean-contemporary'): Promise<Verse[]> {
    try {
      console.log(`BibleService: getVerses 호출 - ${book} ${chapter}장 (${version})`);
      
      // Electron IPC를 통해 실제 데이터베이스에서 가져오기
      if (window.electronAPI && window.electronAPI.getBibleVerses) {
        console.log('Electron API 사용하여 구절 가져오기');
        const verses = await window.electronAPI.getBibleVerses(book, chapter, version);
        console.log('Electron API 응답:', verses ? verses.length : 0, '구절');
        
        if (verses && Array.isArray(verses) && verses.length > 0) {
          // 데이터베이스 응답을 Verse 인터페이스에 맞게 변환
          const convertedVerses: Verse[] = verses.map((verse: any) => ({
            id: verse.id,
            book: verse.book,
            chapter: verse.chapter,
            verse: verse.verse,
            text: verse.text,
            version: verse.version,
            book_order: verse.book_order,
            verse_title: verse.verse_title
          }));
          
          console.log('변환된 구절:', convertedVerses.length, '개');
          return convertedVerses;
        }
      }
      
      console.log('Electron API 사용 불가 또는 응답 없음');
      return [];
    } catch (error) {
      console.error('구절 로드 실패:', error);
      throw new Error(`${book} ${chapter}장 구절을 불러올 수 없습니다: ` + (error as Error).message);
    }
  }

  // 특정 구절 가져오기
  async getVerse(book: string, chapter: number, verse: number, version: string = 'korean-standard'): Promise<Verse | null> {
    try {
      const verses = await this.getVerses(book, chapter, version);
      return verses.find(v => v.verse === verse) || null;
    } catch (error) {
      console.error('구절 로드 실패:', error);
      return null;
    }
  }

  // 특정 장의 주석들 가져오기
  async getCommentaries(book: string, chapter: number): Promise<Commentary[]> {
    try {
      console.log(`BibleService: getCommentaries 호출 - ${book} ${chapter}장`);
      
      // Electron IPC를 통해 실제 데이터베이스에서 가져오기
      if (window.electronAPI && window.electronAPI.getCommentaries) {
        console.log('Electron API 사용하여 주석 가져오기');
        const commentaries = await window.electronAPI.getCommentaries(book, chapter);
        console.log('Electron API 원본 응답 (주석):', commentaries);
        
        if (commentaries && Array.isArray(commentaries)) {
          // 데이터베이스 응답을 Commentary 인터페이스에 맞게 변환
          const convertedCommentaries: Commentary[] = commentaries.map((commentary: any) => ({
            id: commentary.id,
            book: commentary.book_name, // 'book' -> 'book_name'
            chapter: commentary.chapter,
            verse_start: commentary.verse, // 'verse' -> 'verse_start'
            verse_end: commentary.verse,   // 'verse' -> 'verse_end'
            content: commentary.text,      // 'content' -> 'text'
            author: commentary.commentary_name // 'author' -> 'commentary_name'
          }));
          
          console.log('변환된 주석 데이터:', convertedCommentaries);
          return convertedCommentaries;
        }
      }
      
      console.log('Electron API 사용 불가 또는 응답 없음');
      return [];
    } catch (error) {
      console.error('주석 로드 실패:', error);
      return [];
    }
  }

  // 구절 검색
  async searchVerses(query: string, version: string = 'korean-standard'): Promise<Verse[]> {
    try {
      if (window.electronAPI && window.electronAPI.searchVerses) {
        const verses = await window.electronAPI.searchVerses(query, version);
        return verses as Verse[];
      }
      
      return [];
    } catch (error) {
      console.error('구절 검색 실패:', error);
      return [];
    }
  }

  // 사용 가능한 번역본 목록
  async getAvailableVersions(): Promise<{ id: string; name: string }[]> {
    try {
      // 실제 데이터베이스에서 번역본 목록 가져오기
      const versions = await window.electronAPI.getVersions();
      
      // 표시 이름 설정 가져오기
      let displayNames: { [key: string]: string } = {};
      try {
        const displayNamesData = await window.electronAPI.getVersionDisplayNames();
        displayNames = displayNamesData.reduce((acc: any, item: any) => {
          acc[item.version_id] = item.display_name;
          return acc;
        }, {});
      } catch (error) {
        console.warn('표시 이름 로드 실패:', error);
      }

      // 기본 표시 이름 매핑
      const defaultNames: { [key: string]: string } = {
        'korean-standard': '새번역',
        'korean-revised': '개역개정',
        'korean-traditional': '개역한글판',
        'korean-contemporary': '현대인의성경',
        'korean-new-standard': '표준새번역',
        'niv': 'NIV'
      };

      return versions.map((version: any) => ({
        id: version.version,
        name: displayNames[version.version] || defaultNames[version.version] || version.version
      }));
    } catch (error) {
      console.error('번역본 목록 로드 실패:', error);
      return [];
    }
  }
}

// 싱글톤 인스턴스 export
export const bibleService = BibleService.getInstance(); 