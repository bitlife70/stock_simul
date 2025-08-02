-- Initial database setup for Korean Stock Backtesting
-- This script runs when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- Create indexes for better performance
-- These will be created by SQLAlchemy, but we can add additional ones here

-- Create Korean stock market specific functions
CREATE OR REPLACE FUNCTION calculate_korean_trading_days(start_date DATE, end_date DATE)
RETURNS INTEGER AS $$
DECLARE
    trading_days INTEGER;
BEGIN
    -- Calculate trading days excluding weekends
    -- This is a simplified version - in production, should exclude Korean holidays
    SELECT COUNT(*)
    INTO trading_days
    FROM generate_series(start_date, end_date, '1 day'::interval) AS day
    WHERE EXTRACT(DOW FROM day) NOT IN (0, 6); -- Exclude Sunday (0) and Saturday (6)
    
    RETURN trading_days;
END;
$$ LANGUAGE plpgsql;

-- Create function to get latest trading date
CREATE OR REPLACE FUNCTION get_latest_trading_date()
RETURNS DATE AS $$
DECLARE
    latest_date DATE;
BEGIN
    SELECT MAX(date::date) INTO latest_date FROM stock_data;
    RETURN COALESCE(latest_date, CURRENT_DATE - INTERVAL '1 day');
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Insert some initial Korean market data
-- This would be populated by the data collection service

COMMENT ON DATABASE stock_backtesting IS 'Korean Stock Market Backtesting Database';
COMMENT ON FUNCTION calculate_korean_trading_days IS 'Calculate trading days between dates excluding weekends';
COMMENT ON FUNCTION get_latest_trading_date IS 'Get the latest available trading date from stock data';