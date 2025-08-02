/**
 * Korean Character Processing Utilities
 * Handles 한글 초성, 중성, 종성 decomposition for advanced search
 */

// 한글 유니코드 범위
const KOREAN_BASE = 0xAC00;
const KOREAN_END = 0xD7A3;
const CHOSUNG_BASE = 0x1100;
const JUNGSUNG_BASE = 0x1161;
const JONGSUNG_BASE = 0x11A7;

// 초성 리스트 (19개)
const CHOSUNG_LIST = [
  'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ',
  'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
];

// 중성 리스트 (21개)
const JUNGSUNG_LIST = [
  'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ',
  'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ'
];

// 종성 리스트 (28개, 공백 포함)
const JONGSUNG_LIST = [
  '', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ',
  'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ',
  'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
];

/**
 * 한글 문자를 초성, 중성, 종성으로 분해
 */
export function decomposeKorean(char: string): {
  chosung: string;
  jungsung: string;
  jongsung: string;
} | null {
  const code = char.charCodeAt(0);
  
  if (code < KOREAN_BASE || code > KOREAN_END) {
    return null;
  }
  
  const base = code - KOREAN_BASE;
  const chosung = Math.floor(base / 588);
  const jungsung = Math.floor((base % 588) / 28);
  const jongsung = base % 28;
  
  return {
    chosung: CHOSUNG_LIST[chosung] || '',
    jungsung: JUNGSUNG_LIST[jungsung] || '',
    jongsung: JONGSUNG_LIST[jongsung] || ''
  };
}

/**
 * 문자열에서 초성만 추출
 */
export function extractChosung(text: string): string {
  return text
    .split('')
    .map(char => {
      const decomposed = decomposeKorean(char);
      return decomposed ? decomposed.chosung : char;
    })
    .filter(char => char !== '')
    .join('');
}

/**
 * 초성 검색 매칭 (예: "ㅅㅅ" -> "삼성")
 */
export function matchesChosung(text: string, chosungQuery: string): boolean {
  const textChosung = extractChosung(text);
  const normalizedQuery = chosungQuery.replace(/\s+/g, '');
  
  if (normalizedQuery.length === 0) return true;
  if (textChosung.length < normalizedQuery.length) return false;
  
  // 순차적 매칭 (부분 일치 허용)
  let queryIndex = 0;
  for (let i = 0; i < textChosung.length && queryIndex < normalizedQuery.length; i++) {
    if (textChosung[i] === normalizedQuery[queryIndex]) {
      queryIndex++;
    }
  }
  
  return queryIndex === normalizedQuery.length;
}

/**
 * 한글 자음/모음인지 확인
 */
export function isKoreanConsonant(char: string): boolean {
  return CHOSUNG_LIST.includes(char) || 
         JONGSUNG_LIST.includes(char) ||
         /[ㄱ-ㅎ]/.test(char);
}

/**
 * 한글 완성형 문자인지 확인
 */
export function isKoreanSyllable(char: string): boolean {
  const code = char.charCodeAt(0);
  return code >= KOREAN_BASE && code <= KOREAN_END;
}

/**
 * 한글 텍스트 정규화 (공백 제거, 소문자 변환)
 */
export function normalizeKoreanText(text: string): string {
  return text
    .replace(/\s+/g, '')
    .toLowerCase()
    .trim();
}

/**
 * 한글 유사도 계산 (레벤슈타인 거리 기반)
 */
export function koreanSimilarity(a: string, b: string): number {
  const normalizedA = normalizeKoreanText(a);
  const normalizedB = normalizeKoreanText(b);
  
  if (normalizedA === normalizedB) return 1.0;
  
  const maxLength = Math.max(normalizedA.length, normalizedB.length);
  if (maxLength === 0) return 1.0;
  
  const distance = levenshteinDistance(normalizedA, normalizedB);
  return 1 - (distance / maxLength);
}

/**
 * 레벤슈타인 거리 계산
 */
function levenshteinDistance(a: string, b: string): number {
  const matrix = Array(b.length + 1).fill(null).map(() => Array(a.length + 1).fill(null));
  
  for (let i = 0; i <= a.length; i++) matrix[0][i] = i;
  for (let j = 0; j <= b.length; j++) matrix[j][0] = j;
  
  for (let j = 1; j <= b.length; j++) {
    for (let i = 1; i <= a.length; i++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      matrix[j][i] = Math.min(
        matrix[j][i - 1] + 1,     // deletion
        matrix[j - 1][i] + 1,     // insertion
        matrix[j - 1][i - 1] + cost // substitution
      );
    }
  }
  
  return matrix[b.length][a.length];
}

/**
 * 한영 자판 변환 매핑
 */
const KOREAN_TO_ENGLISH_MAP: Record<string, string> = {
  'ㅂ': 'q', 'ㅈ': 'w', 'ㄷ': 'e', 'ㄱ': 'r', 'ㅅ': 't',
  'ㅛ': 'y', 'ㅕ': 'u', 'ㅑ': 'i', 'ㅐ': 'o', 'ㅔ': 'p',
  'ㅁ': 'a', 'ㄴ': 's', 'ㅇ': 'd', 'ㄹ': 'f', 'ㅎ': 'g',
  'ㅗ': 'h', 'ㅓ': 'j', 'ㅏ': 'k', 'ㅣ': 'l',
  'ㅋ': 'z', 'ㅌ': 'x', 'ㅊ': 'c', 'ㅍ': 'v', 'ㅠ': 'b',
  'ㅜ': 'n', 'ㅡ': 'm'
};

const ENGLISH_TO_KOREAN_MAP = Object.fromEntries(
  Object.entries(KOREAN_TO_ENGLISH_MAP).map(([k, v]) => [v, k])
);

/**
 * 한영 자판 오타 교정
 */
export function correctKoreanTypo(text: string): string {
  return text
    .split('')
    .map(char => ENGLISH_TO_KOREAN_MAP[char] || char)
    .join('');
}

/**
 * 영한 자판 오타 교정
 */
export function correctEnglishTypo(text: string): string {
  return text
    .split('')
    .map(char => KOREAN_TO_ENGLISH_MAP[char] || char)
    .join('');
}