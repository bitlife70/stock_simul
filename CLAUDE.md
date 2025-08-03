# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Korean Stock Backtesting Simulation project (`stock_simul`) - a comprehensive web application for simulating trading strategies on KOSPI/KOSDAQ markets.

## Current State - Complete Korean Market Database

**Status**: Complete Korean market coverage implemented, production-ready system
- **Frontend**: Next.js app running on http://localhost:3002 (2,759 stock search support)
- **Backend**: FastAPI server running on http://localhost:8003 (< 5ms search performance)  
- **Database**: 2,759 Korean stocks (KOSPI 962 + KOSDAQ 1,797) with automated daily updates
- **Features**: Complete market search, professional backtesting, advanced analytics
- **GitHub**: https://github.com/bitlife70/stock_simul (125 files, 37,624 lines uploaded)
- **Achievement**: 37x expansion from 74 to 2,759 stocks with 100x performance improvement

## Intelligent Delegation System

**IMPORTANT**: This project uses an automated delegation system. The Project Manager analyzes all requests and automatically delegates to specialized agents without waiting for instructions.

### Available Specialized Agents
1. **automated-trading-advisor**: Korean market APIs, data integration, trading systems
2. **securities-ui-engineer**: Financial UI/UX, charts, Korean localization
3. **stock-trading-expert**: Trading strategies, technical analysis, backtesting
4. **code-reviewer**: Code quality, security, performance optimization
5. **dx-ax-platform-consultant**: Architecture, scalability, developer experience
6. **general-purpose**: Complex research, file operations, multi-step coordination

**See `DELEGATION_SYSTEM.md` for complete delegation rules and coordination protocols.**

## Quick Start Commands

```bash
# Start API Server (Complete Korean Database)
python simple_api.py

# Start Frontend (new terminal)
cd frontend && npm run dev

# Update Stock Database (optional)
python run_batch_update.py
```

**Application URLs**:
- Frontend: http://localhost:3002 (2,759 Korean stocks searchable)
- API Documentation: http://localhost:8003/docs
- Stock Data API: http://localhost:8003/api/v1/stocks
- Health Check: http://localhost:8003/health

## Architecture Overview

- **Frontend**: Next.js 15 + TypeScript + Tailwind CSS + TradingView Charts
- **Backend**: FastAPI + SQLite + Korean market data integration
- **APIs**: FinanceDataReader + pykrx for Korean stock data
- **Localization**: Korean/English support with i18next

## Development Workflow

1. **All requests automatically analyzed and delegated** to appropriate specialists
2. **Progress tracked** in PROGRESS_TRACKER.md with timestamps
3. **Multi-agent coordination** for complex features spanning multiple domains
4. **Quality gates** ensure code review and architectural validation
5. **Korean market focus** with KOSPI/KOSDAQ specific optimizations

## Claude Code Configuration

- Custom permissions in `.claude/settings.local.json` for file system operations
- Automated progress tracking to PROGRESS_TRACKER.md with timestamps
- Intelligent delegation system active for optimal specialist utilization

## Important Guidelines

- **Never create files** unless absolutely necessary - always prefer editing existing files
- **No proactive documentation** creation unless explicitly requested
- **Korean market focus** - all features optimized for KOSPI/KOSDAQ
- **Simulation only** - no real trading integration
- **Quality first** - all changes subject to automated quality gates