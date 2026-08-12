-- NEXUS DATABASE SCHEMA
-- PostgreSQL 12+

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================
-- BUSINESSES
-- ============================================================

CREATE TABLE businesses (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    industry TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_businesses_name ON businesses(name);
CREATE INDEX idx_businesses_uuid ON businesses(uuid);

-- ============================================================
-- CUSTOMERS
-- ============================================================

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    business_id INTEGER REFERENCES businesses(id),
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    notes TEXT,
    total_unpaid DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_customers_business_id ON customers(business_id);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_name ON customers USING GIST(name gist_trgm_ops);

-- ============================================================
-- JOBS
-- ============================================================

CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    business_id INTEGER REFERENCES businesses(id),
    customer_id INTEGER REFERENCES customers(id),
    lot_number TEXT,
    location TEXT,
    description TEXT,
    status TEXT DEFAULT 'new', -- new, scheduled, in_progress, completed, cancelled
    pickup_date DATE,
    pickup_window TEXT, -- e.g., "9am-12pm"
    equipment_type TEXT,
    requires_rigging BOOLEAN DEFAULT false,
    requires_truck BOOLEAN DEFAULT false,
    assigned_rigger TEXT,
    assigned_truck TEXT,
    amount DECIMAL(10, 2) DEFAULT 0,
    paid BOOLEAN DEFAULT false,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_jobs_business_id ON jobs(business_id);
CREATE INDEX idx_jobs_customer_id ON jobs(customer_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_pickup_date ON jobs(pickup_date);
CREATE INDEX idx_jobs_paid ON jobs(paid);

-- ============================================================
-- INVOICES
-- ============================================================

CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    business_id INTEGER REFERENCES businesses(id),
    customer_id INTEGER REFERENCES customers(id),
    invoice_number TEXT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status TEXT DEFAULT 'unpaid', -- unpaid, partial, paid, overdue
    due_date DATE,
    sent_date TIMESTAMP,
    paid_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_invoices_business_id ON invoices(business_id);
CREATE INDEX idx_invoices_customer_id ON invoices(customer_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_due_date ON invoices(due_date);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);

-- ============================================================
-- EMAILS
-- ============================================================

CREATE TABLE emails (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    business_id INTEGER REFERENCES businesses(id),
    customer_id INTEGER REFERENCES customers(id),
    email_from TEXT,
    email_to TEXT,
    subject TEXT,
    body TEXT,
    classification TEXT, -- job, invoice, payment, inquiry, other
    extracted_data JSONB, -- lot number, location, date, etc.
    status TEXT DEFAULT 'unread', -- unread, read, actioned, archived
    processed BOOLEAN DEFAULT false,
    created_task_id INTEGER,
    created_job_id INTEGER,
    action_taken TEXT,
    received_at TIMESTAMP,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_emails_business_id ON emails(business_id);
CREATE INDEX idx_emails_classification ON emails(classification);
CREATE INDEX idx_emails_status ON emails(status);
CREATE INDEX idx_emails_received_at ON emails(received_at);
CREATE INDEX idx_emails_subject ON emails USING GIST(subject gist_trgm_ops);

-- ============================================================
-- TASKS
-- ============================================================

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    business_id INTEGER REFERENCES businesses(id),
    title TEXT NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 3, -- 1=critical, 5=low
    status TEXT DEFAULT 'open', -- open, in_progress, completed, cancelled
    due_date DATE,
    category TEXT, -- email, job, invoice, trading, system
    source TEXT, -- manual, email, job, trading_signal
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_business_id ON tasks(business_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- ============================================================
-- TRADES
-- ============================================================

CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    business_id INTEGER REFERENCES businesses(id),
    symbol TEXT NOT NULL,
    side TEXT NOT NULL, -- LONG, SHORT
    strategy TEXT,
    quantity DECIMAL(10, 4),
    entry_price DECIMAL(12, 2),
    stop_loss DECIMAL(12, 2),
    take_profit DECIMAL(12, 2),
    risk_amount DECIMAL(10, 2),
    status TEXT DEFAULT 'paper_open', -- paper_open, paper_closed, live_open, live_closed
    exit_price DECIMAL(12, 2),
    pnl DECIMAL(10, 2) DEFAULT 0,
    pnl_percent DECIMAL(6, 2) DEFAULT 0,
    commission DECIMAL(10, 2) DEFAULT 0,
    slippage DECIMAL(10, 2) DEFAULT 0,
    opened_at TIMESTAMP,
    closed_at TIMESTAMP,
    hold_time_minutes INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_trades_business_id ON trades(business_id);
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_strategy ON trades(strategy);
CREATE INDEX idx_trades_opened_at ON trades(opened_at);
CREATE INDEX idx_trades_closed_at ON trades(closed_at);

-- ============================================================
-- STRATEGIES
-- ============================================================

CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    business_id INTEGER REFERENCES businesses(id),
    name TEXT NOT NULL, -- Trend Following, Momentum, etc.
    description TEXT,
    asset_class TEXT, -- stocks, crypto, options
    status TEXT DEFAULT 'testing', -- testing, backtested, paper_trading, live, disabled
    backtest_results JSONB, -- sharpe, win_rate, max_drawdown, etc.
    paper_trading_results JSONB,
    live_trading_results JSONB,
    approval_status TEXT DEFAULT 'pending', -- pending, approved, rejected
    approved_by TEXT,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_strategies_business_id ON strategies(business_id);
CREATE INDEX idx_strategies_status ON strategies(status);
CREATE INDEX idx_strategies_approval_status ON strategies(approval_status);

-- ============================================================
-- SIGNALS
-- ============================================================

CREATE TABLE signals (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    business_id INTEGER REFERENCES businesses(id),
    strategy_id INTEGER REFERENCES strategies(id),
    symbol TEXT NOT NULL,
    direction TEXT, -- BUY, SELL, SHORT
    confidence DECIMAL(3, 2), -- 0.00 to 1.00
    entry_price DECIMAL(12, 2),
    stop_price DECIMAL(12, 2),
    target_price DECIMAL(12, 2),
    reason TEXT,
    status TEXT DEFAULT 'generated', -- generated, approved, rejected, executed, expired
    trade_id INTEGER REFERENCES trades(id),
    generated_at TIMESTAMP,
    approved_at TIMESTAMP,
    expired_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_signals_business_id ON signals(business_id);
CREATE INDEX idx_signals_symbol ON signals(symbol);
CREATE INDEX idx_signals_status ON signals(status);
CREATE INDEX idx_signals_generated_at ON signals(generated_at);

-- ============================================================
-- ALERTS
-- ============================================================

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    business_id INTEGER REFERENCES businesses(id),
    category TEXT, -- business, trading, system, security
    severity TEXT DEFAULT 'normal', -- critical, urgent, normal, info
    message TEXT NOT NULL,
    details JSONB,
    acknowledged BOOLEAN DEFAULT false,
    acknowledged_at TIMESTAMP,
    acknowledged_by TEXT,
    sent_to_discord BOOLEAN DEFAULT false,
    sent_to_slack BOOLEAN DEFAULT false,
    sent_to_email BOOLEAN DEFAULT false,
    sent_to_sms BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alerts_business_id ON alerts(business_id);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_category ON alerts(category);
CREATE INDEX idx_alerts_acknowledged ON alerts(acknowledged);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);

-- ============================================================
-- MEMORY SYSTEM (AI Context)
-- ============================================================

CREATE TABLE memory (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    business_id INTEGER REFERENCES businesses(id),
    memory_type TEXT, -- facts, operations, decisions, context, learning
    key TEXT,
    value JSONB,
    confidence DECIMAL(3, 2), -- how certain the system is
    last_updated TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_memory_business_id ON memory(business_id);
CREATE INDEX idx_memory_type ON memory(memory_type);
CREATE INDEX idx_memory_key ON memory(key);

-- ============================================================
-- EVENTS (Audit Log)
-- ============================================================

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    business_id INTEGER REFERENCES businesses(id),
    event_type TEXT, -- email_received, job_created, trade_executed, alert_sent, etc.
    severity TEXT DEFAULT 'info',
    description TEXT,
    details JSONB,
    actor TEXT, -- who/what triggered it (system, user, email, market_scanner, etc.)
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_events_business_id ON events(business_id);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_created_at ON events(created_at);
CREATE INDEX idx_events_severity ON events(severity);

-- ============================================================
-- HEALTH CHECKS
-- ============================================================

CREATE TABLE health_checks (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    business_id INTEGER REFERENCES businesses(id),
    component TEXT, -- database, redis, email, discord, slack, market_feed, broker, aws
    status TEXT, -- healthy, degraded, failed
    message TEXT,
    response_time_ms INTEGER,
    checked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_health_business_id ON health_checks(business_id);
CREATE INDEX idx_health_component ON health_checks(component);
CREATE INDEX idx_health_status ON health_checks(status);
CREATE INDEX idx_health_checked_at ON health_checks(checked_at);

-- ============================================================
-- DEFAULT DATA
-- ============================================================

INSERT INTO businesses (name, description, industry) 
VALUES ('Auction Ready LLC', 'Equipment removal and rigging services', 'Auction & Equipment Services')
ON CONFLICT (name) DO NOTHING;
