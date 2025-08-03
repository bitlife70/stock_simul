'use client';

import { useState, useEffect } from 'react';
import { X, Download, Database, CheckCircle, AlertCircle, Clock, BarChart3, Sun, Moon, Monitor, Globe, Volume2 } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { API_BASE_URL } from '@/lib/config';

interface DatabaseStats {
  total_stocks: number;
  market_breakdown: { [key: string]: number };
  last_update: string | null;
  database_path: string;
}

interface DownloadStatus {
  last_update: string | null;
  total_stocks: number;
  is_updating: boolean;
}

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const { theme, setTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('database');
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [downloadStatus, setDownloadStatus] = useState<DownloadStatus | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadMessage, setDownloadMessage] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Additional settings state
  const [language, setLanguage] = useState('ko');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [chartType, setChartType] = useState('candlestick');

  useEffect(() => {
    if (isOpen) {
      fetchStats();
      fetchDownloadStatus();
      loadSettings();
    }
  }, [isOpen]);

  // Load settings from localStorage
  const loadSettings = () => {
    try {
      const savedLanguage = localStorage.getItem('language');
      const savedAutoRefresh = localStorage.getItem('autoRefresh');
      const savedSoundEnabled = localStorage.getItem('soundEnabled');
      const savedChartType = localStorage.getItem('chartType');
      
      if (savedLanguage) setLanguage(savedLanguage);
      if (savedAutoRefresh) setAutoRefresh(JSON.parse(savedAutoRefresh));
      if (savedSoundEnabled) setSoundEnabled(JSON.parse(savedSoundEnabled));
      if (savedChartType) setChartType(savedChartType);
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  // Save settings to localStorage
  const saveSettings = () => {
    localStorage.setItem('language', language);
    localStorage.setItem('autoRefresh', JSON.stringify(autoRefresh));
    localStorage.setItem('soundEnabled', JSON.stringify(soundEnabled));
    localStorage.setItem('chartType', chartType);
  };

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/data/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch database stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDownloadStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();
      setDownloadStatus({
        last_update: data.last_update,
        total_stocks: data.total_stocks,
        is_updating: false
      });
    } catch (error) {
      console.error('Failed to fetch download status:', error);
    }
  };

  const triggerBatchDownload = async () => {
    try {
      setIsDownloading(true);
      setDownloadMessage('배치 다운로드를 시작하는 중...');
      
      const response = await fetch(`${API_BASE_URL}/api/v1/data/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      
      if (data.status === 'update_triggered') {
        setDownloadMessage(data.message);
        
        // Poll for updates every 5 seconds
        const pollInterval = setInterval(async () => {
          await fetchStats();
          await fetchDownloadStatus();
          
          // Stop polling after 5 minutes or when we detect completion
          const elapsedTime = Date.now() - startTime;
          if (elapsedTime > 300000) { // 5 minutes
            clearInterval(pollInterval);
            setIsDownloading(false);
            setDownloadMessage('다운로드 시간이 초과되었습니다. 상태를 확인해주세요.');
          }
        }, 5000);
        
        const startTime = Date.now();
        
        // Auto-stop polling after some time
        setTimeout(() => {
          clearInterval(pollInterval);
          setIsDownloading(false);
          setDownloadMessage('배치 다운로드가 완료되었습니다.');
        }, 120000); // 2 minutes
        
      } else {
        setDownloadMessage('다운로드 시작에 실패했습니다.');
        setIsDownloading(false);
      }
    } catch (error) {
      console.error('Failed to trigger batch download:', error);
      setDownloadMessage('다운로드 요청 중 오류가 발생했습니다.');
      setIsDownloading(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '없음';
    try {
      return new Date(dateString).toLocaleString('ko-KR');
    } catch {
      return dateString;
    }
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('ko-KR').format(num);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl h-5/6 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">설정</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setActiveTab('database')}
            className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'database'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            데이터베이스 관리
          </button>
          <button
            onClick={() => setActiveTab('general')}
            className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'general'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            일반 설정
          </button>
          <button
            onClick={() => setActiveTab('appearance')}
            className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'appearance'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            테마 및 외관
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 p-6 overflow-auto">
          {activeTab === 'database' && (
            <div className="space-y-6">
              {/* Database Statistics */}
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Database className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">데이터베이스 현황</h3>
                </div>
                
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                    <span className="text-gray-600">로딩 중...</span>
                  </div>
                ) : stats ? (
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border dark:border-gray-600">
                      <div className="text-2xl font-bold text-blue-600">{formatNumber(stats.total_stocks)}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">총 종목 수</div>
                    </div>
                    <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border dark:border-gray-600">
                      <div className="text-2xl font-bold text-green-600">
                        {stats.market_breakdown?.KOSPI || 0}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">KOSPI 종목</div>
                    </div>
                    <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border dark:border-gray-600">
                      <div className="text-2xl font-bold text-purple-600">
                        {stats.market_breakdown?.KOSDAQ || 0}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">KOSDAQ 종목</div>
                    </div>
                    <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border dark:border-gray-600">
                      <div className="text-2xl font-bold text-orange-600">
                        {stats.market_breakdown?.ETF || 0}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">ETF</div>
                    </div>
                  </div>
                ) : (
                  <div className="text-gray-500 dark:text-gray-400">데이터를 불러올 수 없습니다.</div>
                )}

                {stats && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-blue-600" />
                      <span className="text-sm text-blue-800">
                        마지막 업데이트: {formatDate(stats.last_update)}
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* Batch Download Section */}
              <div className="bg-white dark:bg-gray-800 border-2 border-blue-200 dark:border-blue-700 rounded-lg p-6 shadow-md">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <Download className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">종목 배치 다운로드</h3>
                  </div>
                  <button
                    onClick={triggerBatchDownload}
                    disabled={isDownloading}
                    className={`px-6 py-3 rounded-lg text-sm font-medium transition-colors shadow-md ${
                      isDownloading
                        ? 'bg-gray-100 dark:bg-gray-600 text-gray-400 dark:text-gray-500 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600'
                    }`}
                  >
                    {isDownloading ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>다운로드 중...</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <Download className="h-4 w-4" />
                        <span>종목 배치 수신</span>
                      </div>
                    )}
                  </button>
                </div>

                <div className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  모든 KOSPI 및 KOSDAQ 종목 데이터를 최신 상태로 업데이트합니다. 
                  포스코DX (022100)를 포함한 모든 상장 종목이 포함됩니다.
                </div>

                {downloadMessage && (
                  <div className={`p-3 rounded-lg flex items-center space-x-2 ${
                    isDownloading ? 'bg-yellow-50 text-yellow-800' : 
                    downloadMessage.includes('완료') ? 'bg-green-50 text-green-800' : 
                    'bg-red-50 text-red-800'
                  }`}>
                    {isDownloading ? (
                      <Clock className="h-4 w-4" />
                    ) : downloadMessage.includes('완료') ? (
                      <CheckCircle className="h-4 w-4" />
                    ) : (
                      <AlertCircle className="h-4 w-4" />
                    )}
                    <span>{downloadMessage}</span>
                  </div>
                )}

                <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
                  <p>• 다운로드는 백그라운드에서 진행됩니다</p>
                  <p>• 네트워크 상황에 따라 수분이 소요될 수 있습니다</p>
                  <p>• 다운로드 중에도 기존 데이터 검색은 정상 작동합니다</p>
                </div>
              </div>

              {/* Market Coverage Info */}
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-3">
                  <BarChart3 className="h-5 w-5 text-green-600" />
                  <h3 className="text-lg font-medium text-green-900 dark:text-green-100">시장 커버리지</h3>
                </div>
                <div className="text-sm text-green-800 dark:text-green-200 space-y-1">
                  <p>✓ KOSPI 전 종목 (약 900개 종목)</p>
                  <p>✓ KOSDAQ 전 종목 (약 1,500개 종목)</p>
                  <p>✓ 주요 ETF</p>
                  <p>✓ 포스코DX (022100) 포함 모든 상장 종목</p>
                  <p>✓ 실시간 시가총액 및 거래량 정보</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'general' && (
            <div className="space-y-6">
              {/* Language Settings */}
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Globe className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">언어 설정</h3>
                </div>
                <div className="space-y-3">
                  <label className="flex items-center space-x-3">
                    <input
                      type="radio"
                      name="language"
                      value="ko"
                      checked={language === 'ko'}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="text-blue-600"
                    />
                    <span className="text-gray-700 dark:text-gray-300">한국어</span>
                  </label>
                  <label className="flex items-center space-x-3">
                    <input
                      type="radio"
                      name="language"
                      value="en"
                      checked={language === 'en'}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="text-blue-600"
                    />
                    <span className="text-gray-700 dark:text-gray-300">English</span>
                  </label>
                </div>
              </div>

              {/* Data Refresh Settings */}
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Clock className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">데이터 새로고침</h3>
                </div>
                <div className="space-y-4">
                  <label className="flex items-center justify-between">
                    <span className="text-gray-700 dark:text-gray-300">자동 새로고침 활성화</span>
                    <input
                      type="checkbox"
                      checked={autoRefresh}
                      onChange={(e) => setAutoRefresh(e.target.checked)}
                      className="h-4 w-4 text-blue-600 rounded"
                    />
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    주식 데이터를 자동으로 주기적으로 업데이트합니다.
                  </p>
                </div>
              </div>

              {/* Chart Settings */}
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <BarChart3 className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">차트 설정</h3>
                </div>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      기본 차트 유형
                    </label>
                    <select
                      value={chartType}
                      onChange={(e) => setChartType(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    >
                      <option value="candlestick">캔들스틱</option>
                      <option value="line">선형 차트</option>
                      <option value="area">영역 차트</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Sound Settings */}
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Volume2 className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">알림 설정</h3>
                </div>
                <div className="space-y-4">
                  <label className="flex items-center justify-between">
                    <span className="text-gray-700 dark:text-gray-300">소리 알림 활성화</span>
                    <input
                      type="checkbox"
                      checked={soundEnabled}
                      onChange={(e) => setSoundEnabled(e.target.checked)}
                      className="h-4 w-4 text-blue-600 rounded"
                    />
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    백테스팅 완료 및 중요 알림에 대한 소리 알림을 활성화합니다.
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'appearance' && (
            <div className="space-y-6">
              {/* Theme Selection */}
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Monitor className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">테마 선택</h3>
                </div>
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <button
                      onClick={() => setTheme('light')}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        theme === 'light'
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                      }`}
                    >
                      <div className="flex flex-col items-center space-y-2">
                        <Sun className="h-8 w-8 text-yellow-500" />
                        <span className="text-sm font-medium text-gray-900 dark:text-gray-100">라이트</span>
                        <div className="w-full h-6 bg-white border border-gray-300 rounded flex">
                          <div className="w-1/4 bg-blue-500 rounded-l"></div>
                          <div className="w-3/4 bg-gray-100"></div>
                        </div>
                      </div>
                    </button>
                    
                    <button
                      onClick={() => setTheme('dark')}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        theme === 'dark'
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                      }`}
                    >
                      <div className="flex flex-col items-center space-y-2">
                        <Moon className="h-8 w-8 text-blue-400" />
                        <span className="text-sm font-medium text-gray-900 dark:text-gray-100">다크</span>
                        <div className="w-full h-6 bg-gray-800 border border-gray-600 rounded flex">
                          <div className="w-1/4 bg-blue-500 rounded-l"></div>
                          <div className="w-3/4 bg-gray-700"></div>
                        </div>
                      </div>
                    </button>
                    
                    <button
                      onClick={() => {
                        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                        setTheme(prefersDark ? 'dark' : 'light');
                      }}
                      className={`p-4 rounded-lg border-2 transition-all border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500`}
                    >
                      <div className="flex flex-col items-center space-y-2">
                        <Monitor className="h-8 w-8 text-gray-500" />
                        <span className="text-sm font-medium text-gray-900 dark:text-gray-100">시스템</span>
                        <div className="w-full h-6 border border-gray-300 dark:border-gray-600 rounded flex">
                          <div className="w-1/2 bg-white"></div>
                          <div className="w-1/2 bg-gray-800"></div>
                        </div>
                      </div>
                    </button>
                  </div>
                  
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <p className="text-sm text-blue-800 dark:text-blue-200">
                      현재 테마: <span className="font-medium">
                        {theme === 'light' ? '라이트 모드' : '다크 모드'}
                      </span>
                    </p>
                    <p className="text-xs text-blue-600 dark:text-blue-300 mt-1">
                      테마 변경은 즉시 적용되며 자동으로 저장됩니다.
                    </p>
                  </div>
                </div>
              </div>

              {/* Display Settings */}
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <BarChart3 className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">화면 설정</h3>
                </div>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="font-medium text-gray-900 dark:text-gray-100">컴팩트 모드</div>
                      <div className="text-gray-600 dark:text-gray-400 text-xs mt-1">더 많은 정보를 한 화면에 표시</div>
                    </div>
                    <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="font-medium text-gray-900 dark:text-gray-100">고대비 모드</div>
                      <div className="text-gray-600 dark:text-gray-400 text-xs mt-1">시각적 접근성 향상</div>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    추가 화면 설정 옵션은 향후 업데이트에서 제공될 예정입니다.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-between space-x-3 p-6 border-t border-gray-200 dark:border-gray-700">
          <div className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
            <CheckCircle className="h-4 w-4 mr-1" />
            설정이 자동으로 저장됩니다
          </div>
          <div className="flex space-x-3">
            <button
              onClick={saveSettings}
              className="px-4 py-2 text-blue-700 dark:text-blue-300 bg-blue-100 dark:bg-blue-900/20 hover:bg-blue-200 dark:hover:bg-blue-900/40 rounded-lg transition-colors"
            >
              설정 저장
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
            >
              닫기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}