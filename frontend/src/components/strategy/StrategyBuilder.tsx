'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Play, Save, RefreshCw, Settings } from 'lucide-react';
import type { Stock, StrategyTemplate, StrategyFormData } from '@/types';

const strategySchema = z.object({
  name: z.string().min(1, '전략 이름을 입력해주세요'),
  description: z.string().optional(),
  template_id: z.string().min(1, '전략 템플릿을 선택해주세요'),
  parameters: z.record(z.union([z.string(), z.number(), z.boolean()])),
  initial_capital: z.number().min(1000000, '최소 100만원 이상 입력해주세요'),
  start_date: z.string().min(1, '시작 날짜를 선택해주세요'),
  end_date: z.string().min(1, '종료 날짜를 선택해주세요'),
});

interface StrategyBuilderProps {
  selectedStock?: Stock | null;
  onStrategyRun: (strategy: StrategyFormData) => void;
  onStrategySave: (strategy: StrategyFormData) => void;
  loading?: boolean;
}

export default function StrategyBuilder({
  selectedStock,
  onStrategyRun,
  onStrategySave,
  loading = false
}: StrategyBuilderProps) {
  const [templates, setTemplates] = useState<StrategyTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<StrategyTemplate | null>(null);
  const [templatesLoading, setTemplatesLoading] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<StrategyFormData>({
    resolver: zodResolver(strategySchema),
    defaultValues: {
      initial_capital: 10000000,
      start_date: '2023-01-01',
      end_date: '2024-12-31',
      parameters: {},
    }
  });

  const templateId = watch('template_id');

  useEffect(() => {
    fetchTemplates();
  }, []);

  useEffect(() => {
    if (templateId) {
      const template = templates.find(t => t.id === templateId);
      setSelectedTemplate(template || null);
      
      if (template) {
        const defaultParams: Record<string, string | number | boolean> = {};
        Object.entries(template.parameters).forEach(([key, param]) => {
          defaultParams[key] = param.default;
        });
        setValue('parameters', defaultParams);
      }
    }
  }, [templateId, templates, setValue]);

  const fetchTemplates = async () => {
    setTemplatesLoading(true);
    try {
      const response = await fetch('http://localhost:8002/api/v1/strategies/templates');
      const data = await response.json();
      setTemplates(data);
    } catch (error) {
      console.error('전략 템플릿을 가져오는데 실패했습니다:', error);
    } finally {
      setTemplatesLoading(false);
    }
  };

  const onSubmit = (data: StrategyFormData, action: 'run' | 'save') => {
    if (!selectedStock) {
      alert('먼저 종목을 선택해주세요.');
      return;
    }

    if (action === 'run') {
      onStrategyRun(data);
    } else {
      onStrategySave(data);
    }
  };

  const handleReset = () => {
    reset();
    setSelectedTemplate(null);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-800">전략 설정</h2>
        <button
          type="button"
          onClick={handleReset}
          className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          초기화
        </button>
      </div>

      <form className="space-y-6">
        {/* 기본 정보 섹션 */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-700 flex items-center gap-2">
            <Settings className="h-5 w-5" />
            기본 정보
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                전략 이름 *
              </label>
              <input
                {...register('name')}
                type="text"
                placeholder="나만의 투자전략"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900 placeholder-gray-500"
              />
              {errors.name && (
                <p className="text-sm text-red-600 mt-1">{errors.name.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                초기 자본 *
              </label>
              <input
                {...register('initial_capital', { valueAsNumber: true })}
                type="number"
                min="1000000"
                step="1000000"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900 placeholder-gray-500"
              />
              {errors.initial_capital && (
                <p className="text-sm text-red-600 mt-1">{errors.initial_capital.message}</p>
              )}
              <p className="text-xs text-gray-500 mt-1">
                현재 설정: {formatCurrency(watch('initial_capital') || 0)}
              </p>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              전략 설명 (선택사항)
            </label>
            <textarea
              {...register('description')}
              rows={3}
              placeholder="전략에 대한 간단한 설명을 입력해주세요"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900 placeholder-gray-500"
            />
          </div>
        </div>

        {/* 전략 템플릿 선택 */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-700">전략 템플릿</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              템플릿 선택 *
            </label>
            <select
              {...register('template_id')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
              disabled={templatesLoading}
            >
              <option value="">템플릿을 선택해주세요</option>
              {templates.map(template => (
                <option key={template.id} value={template.id}>
                  {template.name_kr} - {template.description}
                </option>
              ))}
            </select>
            {errors.template_id && (
              <p className="text-sm text-red-600 mt-1">{errors.template_id.message}</p>
            )}
          </div>

          {/* 템플릿 매개변수 */}
          {selectedTemplate && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-700 mb-3">매개변수 설정</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(selectedTemplate.parameters).map(([key, param]) => (
                  <div key={key}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {param.description}
                    </label>
                    {param.type === 'number' ? (
                      <input
                        {...register(`parameters.${key}`, { valueAsNumber: true })}
                        type="number"
                        min={param.min}
                        max={param.max}
                        step={param.min !== undefined && param.min < 1 ? 0.01 : 1}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900 placeholder-gray-500"
                      />
                    ) : param.type === 'boolean' ? (
                      <select
                        {...register(`parameters.${key}`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
                      >
                        <option value="true">예</option>
                        <option value="false">아니오</option>
                      </select>
                    ) : (
                      <input
                        {...register(`parameters.${key}`)}
                        type="text"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900 placeholder-gray-500"
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* 백테스팅 기간 */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-700">백테스팅 기간</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                시작 날짜 *
              </label>
              <input
                {...register('start_date')}
                type="date"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
              />
              {errors.start_date && (
                <p className="text-sm text-red-600 mt-1">{errors.start_date.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                종료 날짜 *
              </label>
              <input
                {...register('end_date')}
                type="date"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
              />
              {errors.end_date && (
                <p className="text-sm text-red-600 mt-1">{errors.end_date.message}</p>
              )}
            </div>
          </div>
        </div>

        {/* 선택된 종목 정보 */}
        {selectedStock && (
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-medium text-blue-800 mb-2">선택된 종목</h4>
            <p className="text-blue-700">
              {selectedStock.name_kr} ({selectedStock.symbol}) - {selectedStock.market}
            </p>
          </div>
        )}

        {/* 액션 버튼 */}
        <div className="flex gap-4 pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={handleSubmit((data) => onSubmit(data, 'run'))}
            disabled={loading || isSubmitting || !selectedStock}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                실행중...
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                백테스팅 실행
              </>
            )}
          </button>

          <button
            type="button"
            onClick={handleSubmit((data) => onSubmit(data, 'save'))}
            disabled={isSubmitting}
            className="flex items-center gap-2 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Save className="h-4 w-4" />
            전략 저장
          </button>
        </div>
      </form>
    </div>
  );
}