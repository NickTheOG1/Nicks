"""SQLAlchemy ORM Models for NEXUS"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Boolean,
    Numeric, ForeignKey, JSONB, Index, func, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
import enum

Base = declarative_base()


# ============================================================
# ENUMS
# ============================================================

class JobStatus(str, enum.Enum):
    NEW = "new"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InvoiceStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"


class EmailClassification(str, enum.Enum):
    JOB = "job"
    INVOICE = "invoice"
    PAYMENT = "payment"
    INQUIRY = "inquiry"
    OTHER = "other"


class TaskStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TradeStatus(str, enum.Enum):
    PAPER_OPEN = "paper_open"
    PAPER_CLOSED = "paper_closed"
    LIVE_OPEN = "live_open"
    LIVE_CLOSED = "live_closed"


class StrategyStatus(str, enum.Enum):
    TESTING = "testing"
    BACKTESTED = "backtested"
    PAPER_TRADING = "paper_trading"
    LIVE = "live"
    DISABLED = "disabled"


class SignalStatus(str, enum.Enum):
    GENERATED = "generated"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    EXPIRED = "expired"


class AlertSeverity(str, enum.Enum):
    CRITICAL = "critical"
    URGENT = "urgent"
    NORMAL = "normal"
    INFO = "info"


class HealthStatus(str, enum.Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"


# ============================================================
# BUSINESS
# ============================================================

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    industry = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customers = relationship("Customer", back_populates="business")
    jobs = relationship("Job", back_populates="business")
    invoices = relationship("Invoice", back_populates="business")
    emails = relationship("Email", back_populates="business")
    tasks = relationship("Task", back_populates="business")
    trades = relationship("Trade", back_populates="business")
    strategies = relationship("Strategy", back_populates="business")
    signals = relationship("Signal", back_populates="business")
    alerts = relationship("Alert", back_populates="business")
    memory = relationship("Memory", back_populates="business")
    events = relationship("Event", back_populates="business")
    health_checks = relationship("HealthCheck", back_populates="business")

    def __repr__(self):
        return f"<Business {self.name}>"


# ============================================================
# CUSTOMERS
# ============================================================

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    address = Column(Text)
    notes = Column(Text)
    total_unpaid = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="customers")
    jobs = relationship("Job", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")
    emails = relationship("Email", back_populates="customer")

    __table_args__ = (
        Index("idx_customers_business_id", "business_id"),
        Index("idx_customers_email", "email"),
    )

    def __repr__(self):
        return f"<Customer {self.name}>"


# ============================================================
# JOBS
# ============================================================

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    lot_number = Column(String(255))
    location = Column(Text)
    description = Column(Text)
    status = Column(String(50), default="new")  # new, scheduled, in_progress, completed, cancelled
    pickup_date = Column(Date)
    pickup_window = Column(String(50))  # e.g., "9am-12pm"
    equipment_type = Column(String(255))
    requires_rigging = Column(Boolean, default=False)
    requires_truck = Column(Boolean, default=False)
    assigned_rigger = Column(String(255))
    assigned_truck = Column(String(255))
    amount = Column(Numeric(10, 2), default=0)
    paid = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="jobs")
    customer = relationship("Customer", back_populates="jobs")

    __table_args__ = (
        Index("idx_jobs_business_id", "business_id"),
        Index("idx_jobs_customer_id", "customer_id"),
        Index("idx_jobs_status", "status"),
        Index("idx_jobs_pickup_date", "pickup_date"),
        Index("idx_jobs_paid", "paid"),
    )

    def __repr__(self):
        return f"<Job {self.lot_number} - {self.status}>"


# ============================================================
# INVOICES
# ============================================================

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    invoice_number = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="unpaid")  # unpaid, partial, paid, overdue
    due_date = Column(Date)
    sent_date = Column(DateTime)
    paid_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")

    __table_args__ = (
        Index("idx_invoices_business_id", "business_id"),
        Index("idx_invoices_customer_id", "customer_id"),
        Index("idx_invoices_status", "status"),
        Index("idx_invoices_due_date", "due_date"),
    )

    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.status}>"


# ============================================================
# EMAILS
# ============================================================

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    email_from = Column(String(255))
    email_to = Column(String(255))
    subject = Column(Text)
    body = Column(Text)
    classification = Column(String(50))  # job, invoice, payment, inquiry, other
    extracted_data = Column(JSONB)
    status = Column(String(50), default="unread")  # unread, read, actioned, archived
    processed = Column(Boolean, default=False)
    created_task_id = Column(Integer, ForeignKey("tasks.id"))
    created_job_id = Column(Integer, ForeignKey("jobs.id"))
    action_taken = Column(Text)
    received_at = Column(DateTime)
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="emails")
    customer = relationship("Customer", back_populates="emails")

    __table_args__ = (
        Index("idx_emails_business_id", "business_id"),
        Index("idx_emails_classification", "classification"),
        Index("idx_emails_status", "status"),
        Index("idx_emails_received_at", "received_at"),
    )

    def __repr__(self):
        return f"<Email {self.subject[:50]}>"


# ============================================================
# TASKS
# ============================================================

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(Integer, default=3)  # 1=critical, 5=low
    status = Column(String(50), default="open")  # open, in_progress, completed, cancelled
    due_date = Column(Date)
    category = Column(String(50))  # email, job, invoice, trading, system
    source = Column(String(50))  # manual, email, job, trading_signal
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="tasks")

    __table_args__ = (
        Index("idx_tasks_business_id", "business_id"),
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_priority", "priority"),
        Index("idx_tasks_due_date", "due_date"),
    )

    def __repr__(self):
        return f"<Task {self.title[:30]} - {self.status}>"


# ============================================================
# TRADES
# ============================================================

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # LONG, SHORT
    strategy = Column(String(100))
    quantity = Column(Numeric(10, 4))
    entry_price = Column(Numeric(12, 2))
    stop_loss = Column(Numeric(12, 2))
    take_profit = Column(Numeric(12, 2))
    risk_amount = Column(Numeric(10, 2))
    status = Column(String(50), default="paper_open")  # paper_open, paper_closed, live_open, live_closed
    exit_price = Column(Numeric(12, 2))
    pnl = Column(Numeric(10, 2), default=0)
    pnl_percent = Column(Numeric(6, 2), default=0)
    commission = Column(Numeric(10, 2), default=0)
    slippage = Column(Numeric(10, 2), default=0)
    opened_at = Column(DateTime)
    closed_at = Column(DateTime)
    hold_time_minutes = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="trades")
    signals = relationship("Signal", back_populates="trade")

    __table_args__ = (
        Index("idx_trades_business_id", "business_id"),
        Index("idx_trades_symbol", "symbol"),
        Index("idx_trades_status", "status"),
        Index("idx_trades_strategy", "strategy"),
        Index("idx_trades_opened_at", "opened_at"),
    )

    def __repr__(self):
        return f"<Trade {self.symbol} {self.side} - {self.status}>"


# ============================================================
# STRATEGIES
# ============================================================

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    name = Column(String(100), nullable=False)  # Trend Following, Momentum, etc.
    description = Column(Text)
    asset_class = Column(String(50))  # stocks, crypto, options
    status = Column(String(50), default="testing")  # testing, backtested, paper_trading, live, disabled
    backtest_results = Column(JSONB)  # sharpe, win_rate, max_drawdown, etc.
    paper_trading_results = Column(JSONB)
    live_trading_results = Column(JSONB)
    approval_status = Column(String(50), default="pending")  # pending, approved, rejected
    approved_by = Column(String(255))
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="strategies")
    signals = relationship("Signal", back_populates="strategy")

    __table_args__ = (
        Index("idx_strategies_business_id", "business_id"),
        Index("idx_strategies_status", "status"),
        Index("idx_strategies_approval_status", "approval_status"),
    )

    def __repr__(self):
        return f"<Strategy {self.name} - {self.status}>"


# ============================================================
# SIGNALS
# ============================================================

class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False)  # BUY, SELL, SHORT
    confidence = Column(Numeric(3, 2))  # 0.00 to 1.00
    entry_price = Column(Numeric(12, 2))
    stop_price = Column(Numeric(12, 2))
    target_price = Column(Numeric(12, 2))
    reason = Column(Text)
    status = Column(String(50), default="generated")  # generated, approved, rejected, executed, expired
    trade_id = Column(Integer, ForeignKey("trades.id"))
    generated_at = Column(DateTime)
    approved_at = Column(DateTime)
    expired_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="signals")
    strategy = relationship("Strategy", back_populates="signals")
    trade = relationship("Trade", back_populates="signals")

    __table_args__ = (
        Index("idx_signals_business_id", "business_id"),
        Index("idx_signals_symbol", "symbol"),
        Index("idx_signals_status", "status"),
        Index("idx_signals_generated_at", "generated_at"),
    )

    def __repr__(self):
        return f"<Signal {self.symbol} {self.direction} - {self.status}>"


# ============================================================
# ALERTS
# ============================================================

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    category = Column(String(50))  # business, trading, system, security
    severity = Column(String(50), default="normal")  # critical, urgent, normal, info
    message = Column(Text, nullable=False)
    details = Column(JSONB)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(String(255))
    sent_to_discord = Column(Boolean, default=False)
    sent_to_slack = Column(Boolean, default=False)
    sent_to_email = Column(Boolean, default=False)
    sent_to_sms = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="alerts")

    __table_args__ = (
        Index("idx_alerts_business_id", "business_id"),
        Index("idx_alerts_severity", "severity"),
        Index("idx_alerts_category", "category"),
        Index("idx_alerts_acknowledged", "acknowledged"),
        Index("idx_alerts_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Alert {self.severity} - {self.category}>"


# ============================================================
# MEMORY (AI Context)
# ============================================================

class Memory(Base):
    __tablename__ = "memory"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    memory_type = Column(String(50))  # facts, operations, decisions, context, learning
    key = Column(String(255))
    value = Column(JSONB)
    confidence = Column(Numeric(3, 2))  # how certain the system is
    last_updated = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="memory")

    __table_args__ = (
        Index("idx_memory_business_id", "business_id"),
        Index("idx_memory_type", "memory_type"),
        Index("idx_memory_key", "key"),
    )

    def __repr__(self):
        return f"<Memory {self.memory_type} - {self.key}>"


# ============================================================
# EVENTS (Audit Log)
# ============================================================

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    event_type = Column(String(100))  # email_received, job_created, trade_executed, etc.
    severity = Column(String(50), default="info")
    description = Column(Text)
    details = Column(JSONB)
    actor = Column(String(255))  # who/what triggered it
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="events")

    __table_args__ = (
        Index("idx_events_business_id", "business_id"),
        Index("idx_events_type", "event_type"),
        Index("idx_events_created_at", "created_at"),
        Index("idx_events_severity", "severity"),
    )

    def __repr__(self):
        return f"<Event {self.event_type}>"


# ============================================================
# HEALTH CHECKS
# ============================================================

class HealthCheck(Base):
    __tablename__ = "health_checks"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    component = Column(String(100))  # database, redis, email, discord, slack, market_feed, broker, aws
    status = Column(String(50))  # healthy, degraded, failed
    message = Column(Text)
    response_time_ms = Column(Integer)
    checked_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="health_checks")

    __table_args__ = (
        Index("idx_health_business_id", "business_id"),
        Index("idx_health_component", "component"),
        Index("idx_health_status", "status"),
        Index("idx_health_checked_at", "checked_at"),
    )

    def __repr__(self):
        return f"<HealthCheck {self.component} - {self.status}>"
