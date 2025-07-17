import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
import sqlite3 from 'sqlite3';

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
  app.quit();
}

let mainWindow: BrowserWindow;
let db: sqlite3.Database;

// 책 이름 매핑 함수
const getBookNameMap = (): { [key: string]: string } => {
  return {
    '1': '창세기', '2': '출애굽기', '3': '레위기', '4': '민수기', '5': '신명기',
    '6': '여호수아', '7': '사사기', '8': '룻기', '9': '사무엘상', '10': '사무엘하',
    '11': '열왕기상', '12': '열왕기하', '13': '역대상', '14': '역대하', '15': '에스라',
    '16': '느헤미야', '17': '에스더', '18': '욥기', '19': '시편', '20': '잠언',
    '21': '전도서', '22': '아가', '23': '이사야', '24': '예레미야', '25': '예레미야애가',
    '26': '에스겔', '27': '다니엘', '28': '호세아', '29': '요엘', '30': '아모스',
    '31': '오바댜', '32': '요나', '33': '미가', '34': '나훔', '35': '하박국',
    '36': '스바냐', '37': '학개', '38': '스가랴', '39': '말라기',
    '40': '마태복음', '41': '마가복음', '42': '누가복음', '43': '요한복음', '44': '사도행전',
    '45': '로마서', '46': '고린도전서', '47': '고린도후서', '48': '갈라디아서', '49': '에베소서',
    '50': '빌립보서', '51': '골로새서', '52': '데살로니가전서', '53': '데살로니가후서', '54': '디모데전서',
    '55': '디모데후서', '56': '디도서', '57': '빌레몬서', '58': '히브리서', '59': '야고보서',
    '60': '베드로전서', '61': '베드로후서', '62': '요한일서', '63': '요한이서', '64': '요한삼서',
    '65': '유다서', '66': '요한계시록'
  };
};

// Initialize SQLite database
const initDatabase = () => {
  // 개발 환경과 빌드 환경에서 모두 작동하는 경로
  const dbPath = app.isPackaged 
    ? path.join(process.resourcesPath, 'bible_database.db')
    : path.resolve(__dirname, '..\..\..\paser-app\bible_database.db'); // 개발 환경: paser-app 디렉토리의 DB 사용
  console.log('데이터베이스 경로:', dbPath);
  
  db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
      console.error('데이터베이스 연결 실패:', err);
    } else {
      console.log('성경 데이터베이스 연결 성공');
      // 프롬프트 테이블 생성 및 초기 데이터 삽입
      initPromptTable();
    }
  });
};

// 프롬프트 테이블 초기화 (DB에 이미 데이터가 있으므로 테이블 생성만)
const initPromptTable = () => {
  // 프롬프트 테이블 생성 (이미 존재하면 무시)
  db.run(`
    CREATE TABLE IF NOT EXISTS prompts (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      category TEXT NOT NULL,
      description TEXT NOT NULL,
      content TEXT NOT NULL,
      variables TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `, (err) => {
    if (err) {
      console.error('프롬프트 테이블 생성 실패:', err);
    } else {
      console.log('프롬프트 테이블 확인 완료');
    }
  });
};



const createWindow = (): void => {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    title: '바이블 스튜디오',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    titleBarStyle: 'default',
    show: false,
  });

  // and load the index.html of the app.
  if (process.env.NODE_ENV === 'development' && process.env.WEBPACK_DEV_SERVER) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
    // 개발 중에는 개발자 도구를 열어서 에러 확인
    mainWindow.webContents.openDevTools();
  }

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
app.whenReady().then(() => {
  initDatabase();
  createWindow();

  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed, except on macOS.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (db) {
      db.close();
    }
    app.quit();
  }
});

// Bible Database IPC handlers
ipcMain.handle('get-bible-books', async () => {
  return new Promise((resolve, reject) => {
    // verses 테이블에서 책 목록을 추출 (한국어 book_name 기준)
    db.all(`
      SELECT 
        book_name,
        book_code as book_order,
        CASE 
          WHEN CAST(book_code AS INTEGER) <= 39 THEN '구약'
          ELSE '신약'
        END as testament,
        MAX(chapter) as chapters,
        book_code as id
      FROM verses 
      WHERE book_code > 0
      GROUP BY book_name, book_code
      ORDER BY CAST(book_code AS INTEGER)
    `, (err, rows) => {
      if (err) {
        console.error('get-bible-books 오류:', err);
        reject(err);
      } else {
        console.log('get-bible-books 성공:', rows ? rows.length : 0, '권');
        
        // 책 정보를 정리 (이제 book_name이 이미 한국어임)
        const mappedBooks = rows ? rows.map((row: any) => {
          const bookCode = parseInt(row.book_order) || 0;
          
          return {
            ...row,
            korean_name: row.book_name, // book_name이 이미 한국어
            english_name: row.book_name, // 현재는 한국어만 사용
            book_order: bookCode,
            testament: bookCode <= 39 ? '구약' : '신약'
          };
        }) : [];
        
        resolve(mappedBooks);
      }
    });
  });
});

ipcMain.handle('get-bible-verses', async (event, book: string, chapter: number, version: string = 'korean-contemporary') => {
  return new Promise((resolve, reject) => {
    console.log(`get-bible-verses 요청: ${book} ${chapter}장 (${version})`);
    
    // 한국어 책 이름으로 직접 검색 (모든 book_name이 한국어로 통일됨)
    db.all(`
      SELECT * FROM verses 
      WHERE book_name = ? AND chapter = ? AND version = ?
      ORDER BY verse
    `, [book, chapter, version], (err, rows) => {
      if (err) {
        console.error('get-bible-verses 오류:', err);
        reject(err);
      } else {
        console.log(`get-bible-verses 성공: ${book} ${chapter}장 - ${rows ? rows.length : 0}개 구절`);
        // book 필드를 클라이언트가 기대하는 형태로 설정
        const correctedRows = rows ? rows.map((row: any) => ({
          ...row,
          book: row.book_name // book_name을 book 필드로 복사
        })) : [];
        resolve(correctedRows);
      }
    });
  });
});

ipcMain.handle('get-bible-verse', async (event, book: string, chapter: number, verse: number, version: string = 'korean-contemporary') => {
  return new Promise((resolve, reject) => {
    db.get(`
      SELECT * FROM verses 
      WHERE book_name = ? AND chapter = ? AND verse = ? AND version = ?
    `, [book, chapter, verse, version], (err, row) => {
      if (err) {
        reject(err);
      } else {
        resolve(row);
      }
    });
  });
});

ipcMain.handle('get-commentaries', async (event, book: string, chapter: number) => {
  return new Promise((resolve, reject) => {
    console.log(`get-commentaries 요청: ${book} ${chapter}장`);
    db.all(`
      SELECT * FROM commentaries 
      WHERE book_name = ? AND chapter = ?
      ORDER BY verse
    `, [book, chapter], (err, rows) => {
      if (err) {
        console.error('get-commentaries 오류:', err);
        reject(err);
      } else {
        console.log(`get-commentaries 성공: ${rows ? rows.length : 0}개 주석 반환. 데이터 샘플:`, rows ? rows.slice(0, 2) : '없음');
        resolve(rows);
      }
    });
  });
});

ipcMain.handle('search-verses', async (event, query: string, version: string = 'korean-contemporary') => {
  return new Promise((resolve, reject) => {
    db.all(`
      SELECT * FROM verses 
      WHERE text LIKE ? AND version = ?
      ORDER BY book_code, chapter, verse
      LIMIT 50
    `, [`%${query}%`, version], (err, rows) => {
      if (err) {
        reject(err);
      } else {
        resolve(rows);
      }
    });
  });
});

// Handle AI API calls
ipcMain.handle('generate-sermon-topics', async (event, verseText: string) => {
  // TODO: Implement AI API call
  return [];
});

// Handle sermon draft generation
ipcMain.handle('generate-sermon-draft', async (event, data: any) => {
  // TODO: Implement AI API call with commentary
  return '';
});

// Handle file operations
ipcMain.handle('save-sermon', async (event, sermonData: any) => {
  // TODO: Implement file saving
  return true;
});

ipcMain.handle('load-sermon', async (event, filePath: string) => {
  // TODO: Implement file loading
  return {};
});

// 개발자 API - 번역본 관리
ipcMain.handle('get-versions', async () => {
  return new Promise((resolve, reject) => {
    db.all(`
      SELECT 
        version,
        COUNT(*) as verse_count,
        MIN(book_name) as sample_book,
        MIN(text) as sample_text
      FROM verses 
      GROUP BY version 
      ORDER BY version
    `, (err, rows) => {
      if (err) {
        console.error('get-versions 오류:', err);
        reject(err);
      } else {
        console.log('get-versions 성공:', rows ? rows.length : 0, '개 번역본');
        resolve(rows);
      }
    });
  });
});

ipcMain.handle('delete-version', async (event, versionId: string) => {
  return new Promise((resolve, reject) => {
    db.run(`DELETE FROM verses WHERE version = ?`, [versionId], function(err) {
      if (err) {
        console.error('delete-version 오류:', err);
        reject(err);
      } else {
        console.log(`delete-version 성공: ${versionId} - ${this.changes}개 구절 삭제`);
        resolve(this.changes > 0);
      }
    });
  });
});

ipcMain.handle('update-version-name', async (event, oldVersionId: string, newVersionId: string) => {
  return new Promise((resolve, reject) => {
    db.run(`UPDATE verses SET version = ? WHERE version = ?`, [newVersionId, oldVersionId], function(err) {
      if (err) {
        console.error('update-version-name 오류:', err);
        reject(err);
      } else {
        console.log(`update-version-name 성공: ${oldVersionId} → ${newVersionId} - ${this.changes}개 구절 업데이트`);
        resolve(this.changes > 0);
      }
    });
  });
});

ipcMain.handle('get-version-stats', async (event, versionId: string) => {
  return new Promise((resolve, reject) => {
    db.all(`
      SELECT 
        book_name,
        COUNT(*) as verse_count,
        MIN(chapter) as min_chapter,
        MAX(chapter) as max_chapter
      FROM verses 
      WHERE version = ?
      GROUP BY book_name 
      ORDER BY book_name
    `, [versionId], (err, rows) => {
      if (err) {
        console.error('get-version-stats 오류:', err);
        reject(err);
      } else {
        console.log(`get-version-stats 성공: ${versionId} - ${rows ? rows.length : 0}권`);
        resolve(rows);
      }
    });
  });
});

ipcMain.handle('get-database-info', async () => {
  return new Promise((resolve, reject) => {
    db.all(`
      SELECT 
        'verses' as table_name,
        COUNT(*) as total_rows,
        COUNT(DISTINCT version) as version_count,
        COUNT(DISTINCT book_name) as book_count
      FROM verses
    `, (err, rows) => {
      if (err) {
        console.error('get-database-info 오류:', err);
        reject(err);
      } else {
        console.log('get-database-info 성공:', rows);
        resolve(rows);
      }
    });
  });
});

ipcMain.handle('add-version', async (event, versionData: any) => {
  return new Promise((resolve, reject) => {
    const { versionId, verses } = versionData;
    
    // 트랜잭션으로 모든 구절 삽입
    db.serialize(() => {
      db.run('BEGIN TRANSACTION');
      
      const stmt = db.prepare(`
        INSERT INTO verses (book_name, book_code, chapter, verse, text, version)
        VALUES (?, ?, ?, ?, ?, ?)
      `);
      
      let insertCount = 0;
      let errorOccurred = false;
      
      verses.forEach((verse: any) => {
        stmt.run([
          verse.book_name,
          verse.book_code || 0,
          verse.chapter,
          verse.verse,
          verse.text,
          versionId
        ], function(err) {
          if (err && !errorOccurred) {
            errorOccurred = true;
            db.run('ROLLBACK');
            reject(err);
          } else if (!errorOccurred) {
            insertCount++;
          }
        });
      });
      
      stmt.finalize((err) => {
        if (err || errorOccurred) {
          if (!errorOccurred) {
            db.run('ROLLBACK');
            reject(err);
          }
        } else {
          db.run('COMMIT', (err) => {
            if (err) {
              reject(err);
            } else {
              console.log(`add-version 성공: ${versionId} - ${insertCount}개 구절 추가`);
              resolve(true);
            }
          });
        }
      });
    });
  });
});

// 번역본 표시 이름 관리 API
ipcMain.handle('get-version-display-names', async () => {
  return new Promise((resolve, reject) => {
    // version_display_names 테이블이 없으면 생성
    db.run(`
      CREATE TABLE IF NOT EXISTS version_display_names (
        version_id TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `, (err) => {
      if (err) {
        console.error('version_display_names 테이블 생성 오류:', err);
        reject(err);
        return;
      }
      
      // 표시 이름 목록 가져오기
      db.all(`SELECT * FROM version_display_names ORDER BY version_id`, (err, rows) => {
        if (err) {
          console.error('get-version-display-names 오류:', err);
          reject(err);
        } else {
          console.log('get-version-display-names 성공:', rows ? rows.length : 0, '개');
          resolve(rows);
        }
      });
    });
  });
});

ipcMain.handle('set-version-display-name', async (event, versionId: string, displayName: string) => {
  return new Promise((resolve, reject) => {
    db.run(`
      INSERT OR REPLACE INTO version_display_names (version_id, display_name, updated_at)
      VALUES (?, ?, CURRENT_TIMESTAMP)
    `, [versionId, displayName], function(err) {
      if (err) {
        console.error('set-version-display-name 오류:', err);
        reject(err);
      } else {
        console.log(`set-version-display-name 성공: ${versionId} -> ${displayName}`);
        resolve(true);
      }
    });
  });
});

ipcMain.handle('remove-version-display-name', async (event, versionId: string) => {
  return new Promise((resolve, reject) => {
    db.run(`DELETE FROM version_display_names WHERE version_id = ?`, [versionId], function(err) {
      if (err) {
        console.error('remove-version-display-name 오류:', err);
        reject(err);
      } else {
        console.log(`remove-version-display-name 성공: ${versionId} - ${this.changes}개 삭제`);
        resolve(this.changes > 0);
      }
    });
  });
});

// 프롬프트 관리 API
ipcMain.handle('get-prompts', async () => {
  return new Promise((resolve, reject) => {
    db.all(`
      SELECT id, name, category, description, content, variables, created_at, updated_at
      FROM prompts 
      ORDER BY category, name
    `, (err, rows) => {
      if (err) {
        console.error('get-prompts 오류:', err);
        reject(err);
      } else {
        console.log('get-prompts 성공:', rows ? rows.length : 0, '개 프롬프트');
        // variables 필드를 JSON으로 파싱
        const parsedRows = rows ? rows.map((row: any) => ({
          ...row,
          variables: JSON.parse(row.variables || '[]')
        })) : [];
        resolve(parsedRows);
      }
    });
  });
});

ipcMain.handle('update-prompt', async (event, promptId: string, content: string) => {
  return new Promise((resolve, reject) => {
    db.run(`
      UPDATE prompts 
      SET content = ?, updated_at = CURRENT_TIMESTAMP 
      WHERE id = ?
    `, [content, promptId], function(err) {
      if (err) {
        console.error('update-prompt 오류:', err);
        reject(err);
      } else {
        console.log(`update-prompt 성공: ${promptId} - ${this.changes}개 업데이트`);
        resolve(this.changes > 0);
      }
    });
  });
});

ipcMain.handle('reset-prompt', async (event, promptId: string) => {
  return new Promise((resolve, reject) => {
    // DB에서 원본 프롬프트를 가져와서 초기화 (하드코딩 제거)
    // 실제로는 프롬프트 초기화 기능을 비활성화하거나 별도 로직 필요
    reject(new Error('프롬프트 초기화 기능은 현재 사용할 수 없습니다. DB에서 직접 관리하세요.'));
  });
});

ipcMain.handle('get-prompt', async (event, promptId: string) => {
  return new Promise((resolve, reject) => {
    db.get(`
      SELECT id, name, category, description, content, variables, created_at, updated_at
      FROM prompts 
      WHERE id = ?
    `, [promptId], (err, row: any) => {
      if (err) {
        console.error('get-prompt 오류:', err);
        reject(err);
      } else if (row) {
        console.log(`get-prompt 성공: ${promptId}`);
        // variables 필드를 JSON으로 파싱
        const parsedRow = {
          ...row,
          variables: JSON.parse(row.variables || '[]')
        };
        resolve(parsedRow);
      } else {
        console.log(`get-prompt 실패: ${promptId} - 프롬프트를 찾을 수 없음`);
        resolve(null);
      }
    });
  });
}); 