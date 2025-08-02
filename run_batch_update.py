#!/usr/bin/env python3
"""
Korean Stock Data Batch Updater
일일 배치 업데이트를 수동으로 실행하는 스크립트
"""

import asyncio
import sys
from datetime import datetime
from stock_data_manager import stock_manager, daily_batch_update

async def main():
    print("🔄 Korean Stock Data Batch Updater")
    print("=" * 50)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 현재 상태 확인
    stats = stock_manager.get_stats()
    print("📊 Current Database Status:")
    print(f"  Total Stocks: {stats['total_stocks']:,}")
    print(f"  Markets: {stats['market_breakdown']}")
    print(f"  Last Update: {stats['last_update'] or 'Never'}")
    print()

    # 업데이트 필요 여부 확인
    should_update = stock_manager.should_update()
    if not should_update and len(sys.argv) < 2:
        print("ℹ️  Database is up to date (updated within 24 hours)")
        print("   Use 'python run_batch_update.py --force' to force update")
        return

    force_update = '--force' in sys.argv
    if force_update:
        print("🔥 Force update requested")

    try:
        print("🚀 Starting batch download...")
        print("   This may take 5-15 minutes depending on network speed")
        print()

        result = await daily_batch_update()
        
        print()
        print("✅ Batch Update Results:")
        print(f"  Status: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'success':
            print(f"  Total Stocks Downloaded: {result.get('total_stocks', 0):,}")
            print(f"  Success Count: {result.get('success_count', 0):,}")
            print(f"  Duration: {result.get('duration_seconds', 0):.1f} seconds")
            print(f"  Data Hash: {result.get('data_hash', 'N/A')[:8]}...")
        elif result.get('status') == 'skipped':
            print(f"  Reason: {result.get('reason', 'unknown')}")

        # 최종 상태 확인
        print()
        final_stats = stock_manager.get_stats()
        print("📊 Final Database Status:")
        print(f"  Total Stocks: {final_stats['total_stocks']:,}")
        print(f"  Markets: {final_stats['market_breakdown']}")
        print(f"  Last Update: {final_stats['last_update']}")

        # 샘플 검색 테스트
        print()
        print("🔍 Quick Search Test:")
        test_queries = ["삼성", "게임", "바이오", "NAVER"]
        for query in test_queries:
            results = stock_manager.search_stocks(query, 3)
            print(f"  '{query}': {len(results)} results")
            for stock in results[:2]:  # Show first 2 results
                print(f"    - {stock['name_kr']} ({stock['symbol']}, {stock['market']})")

    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print()
    print("🎉 Batch update completed successfully!")
    print("   API server will now serve the updated data")

if __name__ == "__main__":
    asyncio.run(main())