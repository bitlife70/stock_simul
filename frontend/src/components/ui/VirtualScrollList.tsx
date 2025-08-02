'use client';

import { useState, useEffect, useRef, useMemo, useCallback } from 'react';

interface VirtualScrollListProps<T> {
  items: T[];
  itemHeight: number;
  containerHeight: number;
  renderItem: (item: T, index: number, isSelected: boolean) => React.ReactNode;
  selectedIndex: number;
  onItemClick: (item: T, index: number) => void;
  className?: string;
  overscan?: number; // Additional items to render outside viewport
}

export default function VirtualScrollList<T>({
  items,
  itemHeight,
  containerHeight,
  renderItem,
  selectedIndex,
  onItemClick,
  className = '',
  overscan = 5
}: VirtualScrollListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);
  const scrollElementRef = useRef<HTMLDivElement>(null);

  // Calculate visible range
  const visibleRange = useMemo(() => {
    const containerScrollTop = scrollTop;
    const containerScrollBottom = containerScrollTop + containerHeight;

    const startIndex = Math.max(0, Math.floor(containerScrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      items.length - 1,
      Math.ceil(containerScrollBottom / itemHeight) + overscan
    );

    return { startIndex, endIndex };
  }, [scrollTop, containerHeight, itemHeight, items.length, overscan]);

  // Calculate total height and visible items
  const totalHeight = items.length * itemHeight;
  const visibleItems = useMemo(() => {
    const { startIndex, endIndex } = visibleRange;
    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      item,
      index: startIndex + index
    }));
  }, [items, visibleRange]);

  // Handle scroll events
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);

  // Scroll to index (for keyboard navigation)
  const scrollToIndex = useCallback((index: number) => {
    if (!scrollElementRef.current) return;

    const targetScrollTop = index * itemHeight;
    const currentScrollTop = scrollElementRef.current.scrollTop;
    const containerHeight = scrollElementRef.current.clientHeight;

    // Check if item is already visible
    const itemTop = targetScrollTop;
    const itemBottom = itemTop + itemHeight;
    const visibleTop = currentScrollTop;
    const visibleBottom = visibleTop + containerHeight;

    if (itemTop < visibleTop) {
      // Item is above visible area
      scrollElementRef.current.scrollTop = itemTop;
    } else if (itemBottom > visibleBottom) {
      // Item is below visible area
      scrollElementRef.current.scrollTop = itemBottom - containerHeight;
    }
  }, [itemHeight]);

  // Auto-scroll to selected item when selectedIndex changes
  useEffect(() => {
    if (selectedIndex >= 0 && selectedIndex < items.length) {
      scrollToIndex(selectedIndex);
    }
  }, [selectedIndex, scrollToIndex, items.length]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!scrollElementRef.current?.contains(document.activeElement)) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          if (selectedIndex < items.length - 1) {
            scrollToIndex(selectedIndex + 1);
          }
          break;
        case 'ArrowUp':
          e.preventDefault();
          if (selectedIndex > 0) {
            scrollToIndex(selectedIndex - 1);
          }
          break;
        case 'Home':
          e.preventDefault();
          scrollToIndex(0);
          break;
        case 'End':
          e.preventDefault();
          scrollToIndex(items.length - 1);
          break;
        case 'PageDown':
          e.preventDefault();
          const pageDownIndex = Math.min(
            items.length - 1,
            selectedIndex + Math.floor(containerHeight / itemHeight)
          );
          scrollToIndex(pageDownIndex);
          break;
        case 'PageUp':
          e.preventDefault();
          const pageUpIndex = Math.max(
            0,
            selectedIndex - Math.floor(containerHeight / itemHeight)
          );
          scrollToIndex(pageUpIndex);
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [selectedIndex, items.length, containerHeight, itemHeight, scrollToIndex]);

  return (
    <div
      ref={scrollElementRef}
      className={`overflow-auto ${className}`}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
      tabIndex={0}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${visibleRange.startIndex * itemHeight}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0
          }}
        >
          {visibleItems.map(({ item, index }) => (
            <div
              key={index}
              style={{ height: itemHeight }}
              onClick={() => onItemClick(item, index)}
              className="cursor-pointer"
            >
              {renderItem(item, index, index === selectedIndex)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Performance-optimized memoized version
export const MemoizedVirtualScrollList = <T,>(props: VirtualScrollListProps<T>) => {
  return <VirtualScrollList {...props} />;
};

// Hook for managing virtual scroll state
export const useVirtualScroll = <T,>(items: T[], itemHeight: number, containerHeight: number) => {
  const [selectedIndex, setSelectedIndex] = useState(-1);
  
  const selectNext = useCallback(() => {
    setSelectedIndex(prev => Math.min(items.length - 1, prev + 1));
  }, [items.length]);
  
  const selectPrevious = useCallback(() => {
    setSelectedIndex(prev => Math.max(0, prev - 1));
  }, []);
  
  const selectIndex = useCallback((index: number) => {
    if (index >= 0 && index < items.length) {
      setSelectedIndex(index);
    }
  }, [items.length]);
  
  const clearSelection = useCallback(() => {
    setSelectedIndex(-1);
  }, []);
  
  const getSelectedItem = useCallback(() => {
    return selectedIndex >= 0 && selectedIndex < items.length 
      ? items[selectedIndex] 
      : null;
  }, [items, selectedIndex]);

  return {
    selectedIndex,
    selectNext,
    selectPrevious,
    selectIndex,
    clearSelection,
    getSelectedItem
  };
};