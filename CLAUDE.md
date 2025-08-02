# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Korean Stock Backtesting Simulation project (`stock_simul`) - a comprehensive web application for simulating trading strategies on KOSPI/KOSDAQ markets.

## Current State - Week 2: Enhanced Data Integration

**Status**: UI components complete, API server functional, ready for enhanced features
- **Frontend**: Next.js app running on http://localhost:3002
- **Backend**: FastAPI server running on http://localhost:8001  
- **Features**: Stock search, chart display, strategy builder, backtest execution
- **Next Phase**: Real-time data integration and advanced backtesting features

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
# Start API Server
python api_server.py

# Start Frontend (new terminal)
cd frontend && npm run dev
```

**Application URLs**:
- Frontend: http://localhost:3002
- API Documentation: http://localhost:8001/docs
- Stock Data API: http://localhost:8001/api/v1/stocks

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