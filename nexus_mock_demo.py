"""
NEXUS MOCK SYSTEM DEMO
=====================

This is a fully functional MOCK system that shows you:
- How the AI orchestrator works
- How the permission system operates
- How business automation flows
- How trading decisions are made
- What alerts/dashboards look like
- How memory and context work

Run this file to see NEXUS in action (simulated).

Install:
    pip install colorama tabulate

Then run:
    python nexus_mock_demo.py
"""

import json
import time
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any
from colorama import Fore, Back, Style, init

init(autoreset=True)


# ============================================================
# PERMISSION SYSTEM
# ============================================================

class PermissionLevel(Enum):
    """NEXUS Permission Hierarchy"""
    LEVEL_0_OBSERVE = 0           # Read, analyze, monitor
    LEVEL_1_RECOMMEND = 1         # Draft suggestions
    LEVEL_2_LOW_RISK = 2          # Create tasks, notifications
    LEVEL_3_BUSINESS = 3          # Send approved communications
    LEVEL_4_FINANCIAL = 4         # Brokerage orders (requires approval)
    LEVEL_5_NEVER = 5             # Locked forever


class ActionRequest:
    """Represents an action NEXUS wants to take"""

    def __init__(self, action_type, description, permission_level, details):
        self.action_type = action_type
        self.description = description
        self.permission_level = permission_level
        self.details = details
        self.approved = False
        self.executed = False

    def __repr__(self):
        status = "✓ EXECUTED" if self.executed else ("✓ APPROVED" if self.approved else "⧖ PENDING")
        return f"[{status}] {self.action_type}: {self.description}"


# ============================================================
# MEMORY SYSTEM
# ============================================================

class MemorySystem:
    """NEXUS keeps track of everything"""

    def __init__(self):
        self.permanent_facts = {
            "business_name": "NickTheOG1 Equipment Services",
            "business_type": "Equipment removal & rigging",
            "customers": {
                "ABC Auctions": {"email": "info@abcauctions.com", "unpaid": 2420},
                "XYZ Demolition": {"email": "contact@xyzdemolition.com", "unpaid": 0},
                "Local Estate Sales": {"email": "sales@localestatesales.com", "unpaid": 5800},
            },
            "vendors": {
                "Prime Rigging": {"phone": "(555) 123-4567", "rate": "Hourly + equipment"},
                "QuickHaul Transport": {"phone": "(555) 987-6543", "rate": "$1.50/mile"},
            },
            "locations": {
                "Main Yard": "1200 Harmon Road",
                "Staging": "847 Industrial Ave",
            }
        }

        self.operational_state = {
            "open_jobs": 17,
            "scheduled_pickups": 6,
            "unpaid_invoices": 8420,
            "revenue_potential": 14730,
            "active_trades": 3,
            "paper_account_value": 102184,
            "today_pnl": 184,
        }

        self.decision_log = [
            {
                "timestamp": "2026-08-12 09:15",
                "decision": "Email from ABC Auctions detected. Lot 42 requires rigging.",
                "action_taken": "Classified as Priority 1. Drafted response. Awaiting approval.",
            },
            {
                "timestamp": "2026-08-12 08:42",
                "decision": "Market scan detected oversold condition in QQQ.",
                "action_taken": "Mean reversion strategy generated BUY signal. Backtested. Approved for paper trade.",
            },
            {
                "timestamp": "2026-08-12 07:00",
                "decision": "Daily health check passed.",
                "action_taken": "All systems online. Backups healthy.",
            },
        ]

        self.trading_memory = {
            "strategies_active": ["Trend Following", "Momentum", "Mean Reversion"],
            "strategies_testing": ["Volatility Breakout", "Market Regime Adaptive"],
            "best_performer": "Trend Following (Sharpe: 1.8, Win rate: 58%)",
            "current_exposure": "1.1% of account",
            "daily_loss_limit": "2.0%",
            "daily_loss_used": "0.3%",
        }

    def get_context(self):
        """Return current full context"""
        return {
            "facts": self.permanent_facts,
            "operations": self.operational_state,
            "decisions": self.decision_log[-3:],  # Last 3 decisions
            "trading": self.trading_memory,
        }


# ============================================================
# EVENT PROCESSOR
# ============================================================

@dataclass
class Event:
    """Something happened in the world"""
    event_type: str  # email, calendar, market_data, alert, etc.
    source: str
    timestamp: str
    content: Dict[str, Any]
    importance: int  # 1-10


class EventProcessor:
    """NEXUS processes incoming events"""

    def __init__(self, memory: MemorySystem):
        self.memory = memory
        self.events_processed = 0
        self.actions_created = []

    def process(self, event: Event) -> List[ActionRequest]:
        """
        Event → Classify → Determine Importance → Check Context → Decide Action
        """
        self.events_processed += 1

        print(f"\n{Fore.CYAN}[EVENT PROCESSOR]{Style.RESET_ALL}")
        print(f"  Type: {event.event_type}")
        print(f"  Source: {event.source}")
        print(f"  Timestamp: {event.timestamp}")
        print(f"  Content: {event.content}")

        actions = []

        # ========== EMAIL EVENT ==========
        if event.event_type == "email":

            email = event.content
            subject = email.get("subject", "").lower()
            body = email.get("body", "").lower()
            sender = email.get("from", "")

            print(f"\n{Fore.YELLOW}→ CLASSIFYING EMAIL{Style.RESET_ALL}")

            # Detect what this email is about
            classifications = []
            if "pickup" in subject or "pickup" in body:
                classifications.append("PICKUP_REQUEST")
            if "lot" in subject or "lot" in body:
                classifications.append("JOB_LISTING")
            if "invoice" in subject or "payment" in subject:
                classifications.append("INVOICE/PAYMENT")
            if "unpaid" in body:
                classifications.append("UNPAID_ALERT")

            print(f"  Classifications: {classifications}")

            # Check context
            print(f"\n{Fore.YELLOW}→ CHECKING CONTEXT{Style.RESET_ALL}")
            context = self.memory.get_context()
            customer = None
            for cust_name in context["facts"]["customers"]:
                if cust_name.lower() in sender.lower():
                    customer = cust_name
                    print(f"  Found customer: {customer}")
                    break

            # Determine action
            print(f"\n{Fore.YELLOW}→ DETERMINING ACTION{Style.RESET_ALL}")

            if "PICKUP_REQUEST" in classifications:
                action = ActionRequest(
                    action_type="CREATE_JOB",
                    description=f"Schedule pickup for {customer or sender}",
                    permission_level=PermissionLevel.LEVEL_2_LOW_RISK,
                    details={
                        "customer": customer or sender,
                        "lot": email.get("lot", "Unknown"),
                        "location": email.get("location", "TBD"),
                        "date_requested": email.get("date", "ASAP"),
                    }
                )
                actions.append(action)
                print(f"  → Created: {action}")

            if "UNPAID_ALERT" in classifications and customer:
                outstanding = context["facts"]["customers"].get(customer, {}).get("unpaid", 0)
                if outstanding > 0:
                    action = ActionRequest(
                        action_type="SEND_PAYMENT_REMINDER",
                        description=f"Send payment reminder to {customer}",
                        permission_level=PermissionLevel.LEVEL_3_BUSINESS,
                        details={
                            "customer": customer,
                            "amount": outstanding,
                            "tone": "professional but firm",
                        }
                    )
                    actions.append(action)
                    print(f"  → Created: {action}")

        # ========== MARKET DATA EVENT ==========
        elif event.event_type == "market_data":

            market = event.content
            symbol = market.get("symbol")
            signal = market.get("signal")
            confidence = market.get("confidence", 0)

            print(f"\n{Fore.YELLOW}→ EVALUATING TRADING SIGNAL{Style.RESET_ALL}")
            print(f"  Symbol: {symbol}")
            print(f"  Signal: {signal}")
            print(f"  Confidence: {confidence:.0%}")

            if confidence > 0.65:
                action = ActionRequest(
                    action_type="EXECUTE_PAPER_TRADE",
                    description=f"Paper trade: {signal} {symbol} (confidence {confidence:.0%})",
                    permission_level=PermissionLevel.LEVEL_2_LOW_RISK,
                    details={
                        "symbol": symbol,
                        "side": "LONG" if signal == "BUY" else "SHORT",
                        "strategy": market.get("strategy", "Unknown"),
                        "entry": market.get("entry", 0),
                        "stop": market.get("stop", 0),
                        "target": market.get("target", 0),
                        "confidence": confidence,
                    }
                )
                actions.append(action)
                print(f"  → Created: {action}")

        # ========== ALERT EVENT ==========
        elif event.event_type == "health_alert":

            alert = event.content
            severity = alert.get("severity")

            print(f"\n{Fore.YELLOW}→ PROCESSING ALERT{Style.RESET_ALL}")
            print(f"  Severity: {severity}")
            print(f"  Message: {alert.get('message')}")

            if severity == "CRITICAL":
                action = ActionRequest(
                    action_type="NOTIFY_USER",
                    description=f"CRITICAL ALERT: {alert.get('message')}",
                    permission_level=PermissionLevel.LEVEL_0_OBSERVE,
                    details=alert
                )
                actions.append(action)

        self.actions_created.extend(actions)
        return actions


# ============================================================
# PERMISSION ENFORCER
# ============================================================

class PermissionEnforcer:
    """NEXUS respects authority levels"""

    def __init__(self):
        self.approvals = {}
        self.auto_approve_levels = [
            PermissionLevel.LEVEL_0_OBSERVE,
            PermissionLevel.LEVEL_2_LOW_RISK,  # Low-risk automation
        ]

    def evaluate(self, action: ActionRequest) -> bool:
        """
        Decide if action should be auto-approved or needs human approval
        """
        print(f"\n{Fore.MAGENTA}[PERMISSION CHECK]{Style.RESET_ALL}")
        print(f"  Action: {action.action_type}")
        print(f"  Required level: {action.permission_level.name}")

        # Auto-approved actions
        if action.permission_level in self.auto_approve_levels:
            print(f"  {Fore.GREEN}✓ AUTO-APPROVED (low risk){Style.RESET_ALL}")
            action.approved = True
            return True

        # Actions requiring human approval
        if action.permission_level == PermissionLevel.LEVEL_1_RECOMMEND:
            print(f"  {Fore.YELLOW}⧖ NEEDS REVIEW (recommendation){Style.RESET_ALL}")
            return False

        if action.permission_level == PermissionLevel.LEVEL_3_BUSINESS:
            print(f"  {Fore.YELLOW}⧖ NEEDS APPROVAL (business action){Style.RESET_ALL}")
            return False

        if action.permission_level == PermissionLevel.LEVEL_4_FINANCIAL:
            print(f"  {Fore.RED}⧖ REQUIRES EXPLICIT APPROVAL (financial){Style.RESET_ALL}")
            return False

        if action.permission_level == PermissionLevel.LEVEL_5_NEVER:
            print(f"  {Fore.RED}✗ DENIED (blocked forever){Style.RESET_ALL}")
            return False

        return False

    def execute(self, action: ActionRequest):
        """Execute approved action"""
        if not action.approved:
            print(f"  {Fore.RED}Cannot execute unapproved action{Style.RESET_ALL}")
            return

        print(f"\n{Fore.GREEN}[EXECUTING ACTION]{Style.RESET_ALL}")
        print(f"  {action.action_type}")
        print(f"  Details: {json.dumps(action.details, indent=2)}")

        action.executed = True
        print(f"  {Fore.GREEN}✓ EXECUTED{Style.RESET_ALL}")


# ============================================================
# DASHBOARD
# ============================================================

def print_dashboard(memory: MemorySystem, processor: EventProcessor, actions: List[ActionRequest]):
    """Display NEXUS command center"""

    ops = memory.operational_state
    trading = memory.trading_memory

    print(f"\n{Back.BLUE}{Fore.WHITE}{'='*70}{Style.RESET_ALL}")
    print(f"{Back.BLUE}{Fore.WHITE}{'NEXUS COMMAND CENTER':^70}{Style.RESET_ALL}")
    print(f"{Back.BLUE}{Fore.WHITE}{'='*70}{Style.RESET_ALL}")

    # SYSTEM STATUS
    print(f"\n{Fore.CYAN}SYSTEM STATUS{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}● ONLINE{Style.RESET_ALL}  |  Uptime: 37d 14h  |  Workers: 12/12  |  Database: HEALTHY")

    # BUSINESS
    print(f"\n{Fore.CYAN}BUSINESS{Style.RESET_ALL}")
    print(f"  Open jobs:              {ops['open_jobs']}")
    print(f"  Unscheduled:            {ops['scheduled_pickups']}")
    print(f"  Unpaid invoices:        ${ops['unpaid_invoices']:,}")
    print(f"  Potential revenue:      ${ops['revenue_potential']:,}")

    # TRADING
    print(f"\n{Fore.CYAN}TRADING{Style.RESET_ALL}")
    print(f"  Mode:                   PAPER")
    print(f"  Open positions:         {ops['active_trades']}")
    print(f"  Today's P/L:            {Fore.GREEN}+${ops['today_pnl']}{Style.RESET_ALL}")
    print(f"  Account value:          ${ops['paper_account_value']:,}")
    print(f"  Risk deployed:          {trading['current_exposure']}")
    print(f"  Daily loss limit:       {trading['daily_loss_limit']}")
    print(f"  Active strategies:      {', '.join(trading['strategies_active'])}")
    print(f"  Best performer:         {trading['best_performer']}")

    # AUTOMATION
    print(f"\n{Fore.CYAN}AUTOMATION{Style.RESET_ALL}")
    print(f"  Events processed:       {processor.events_processed}")
    print(f"  Actions created:        {len(processor.actions_created)}")
    pending = sum(1 for a in processor.actions_created if not a.approved)
    executed = sum(1 for a in processor.actions_created if a.executed)
    print(f"  Pending approval:       {pending}")
    print(f"  Executed:               {executed}")

    # ALERTS
    print(f"\n{Fore.CYAN}RECENT ACTIONS{Style.RESET_ALL}")
    for action in actions[-3:]:
        if action.executed:
            icon = f"{Fore.GREEN}✓{Style.RESET_ALL}"
        elif action.approved:
            icon = f"{Fore.YELLOW}→{Style.RESET_ALL}"
        else:
            icon = f"{Fore.YELLOW}⧖{Style.RESET_ALL}"
        print(f"  {icon} {action.action_type}: {action.description}")

    print(f"\n{Back.BLUE}{Fore.WHITE}{'='*70}{Style.RESET_ALL}")


# ============================================================
# TRADING STRATEGY SHOWCASE
# ============================================================

def show_trading_strategy_example():
    """Show how multiple strategies work together"""

    print(f"\n{Back.GREEN}{Fore.WHITE}{'='*70}{Style.RESET_ALL}")
    print(f"{Back.GREEN}{Fore.WHITE}{'TRADING STRATEGY EXECUTION FLOW':^70}{Style.RESET_ALL}")
    print(f"{Back.GREEN}{Fore.WHITE}{'='*70}{Style.RESET_ALL}")

    strategies = {
        "Trend Following": {
            "signal": "BUY",
            "symbol": "SPY",
            "confidence": 0.72,
            "reason": "Price > 200MA, uptrend intact",
            "backtest_sharpe": 1.8,
            "backtest_winrate": 0.58,
        },
        "Mean Reversion": {
            "signal": "BUY",
            "symbol": "QQQ",
            "confidence": 0.68,
            "reason": "RSI oversold, price 2 std dev below MA",
            "backtest_sharpe": 1.2,
            "backtest_winrate": 0.52,
        },
        "Momentum": {
            "signal": "SKIP",
            "symbol": "NVDA",
            "confidence": 0.35,
            "reason": "Insufficient volume expansion",
            "backtest_sharpe": 0.9,
            "backtest_winrate": 0.51,
        },
    }

    for strat_name, data in strategies.items():
        print(f"\n{Fore.CYAN}{strat_name}{Style.RESET_ALL}")
        print(f"  Signal:           {data['signal']}")
        print(f"  Symbol:           {data['symbol']}")
        print(f"  Confidence:       {data['confidence']:.0%}")
        print(f"  Reason:           {data['reason']}")
        print(f"  Backtest Sharpe:  {data['backtest_sharpe']}")
        print(f"  Win Rate:         {data['backtest_winrate']:.0%}")

        if data['signal'] != "SKIP" and data['confidence'] > 0.65:
            print(f"  {Fore.GREEN}→ APPROVED FOR PAPER TRADE{Style.RESET_ALL}")
        elif data['signal'] == "SKIP":
            print(f"  {Fore.YELLOW}→ FILTERED OUT (low confidence){Style.RESET_ALL}")

    print(f"\n{Back.GREEN}{Fore.WHITE}{'='*70}{Style.RESET_ALL}")


# ============================================================
# SLACK/DISCORD ALERTS
# ============================================================

def show_alert_examples():
    """Show how alerts would appear in real integrations"""

    print(f"\n{Back.MAGENTA}{Fore.WHITE}{'='*70}{Style.RESET_ALL}")
    print(f"{Back.MAGENTA}{Fore.WHITE}{'SLACK/DISCORD ALERT EXAMPLES':^70}{Style.RESET_ALL}")
    print(f"{Back.MAGENTA}{Fore.WHITE}{'='*70}{Style.RESET_ALL}")

    alerts = [
        {
            "channel": "Slack #business",
            "severity": "NORMAL",
            "message": "📧 Email from ABC Auctions: Lot 42 pickup requested Friday. Requires rigging approval.",
        },
        {
            "channel": "Discord #trading",
            "severity": "INFO",
            "message": "📈 Mean Reversion strategy: BUY QQQ @ 387.50 | Stop 385.20 | Target 392.30 | Confidence 68%",
        },
        {
            "channel": "Email (important)",
            "severity": "URGENT",
            "message": "⚠️  INVOICE ALERT: XYZ Corp still owes $5,800. Invoice 30 days overdue.",
        },
        {
            "channel": "Discord #system",
            "severity": "NORMAL",
            "message": "✓ Daily health check passed. All systems online. Backups healthy.",
        },
    ]

    for alert in alerts:
        print(f"\n{alert['channel']}")
        print(f"  Severity: {alert['severity']}")
        print(f"  {alert['message']}")

    print(f"\n{Back.MAGENTA}{Fore.WHITE}{'='*70}{Style.RESET_ALL}")


# ============================================================
# MAIN DEMO
# ============================================================

def main():
    """Run the mock system demo"""

    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{'NEXUS MOCK SYSTEM DEMO':^70}")
    print(f"{'='*70}{Style.RESET_ALL}\n")

    # Initialize
    memory = MemorySystem()
    processor = EventProcessor(memory)
    enforcer = PermissionEnforcer()

    # Create sample events
    events = [
        Event(
            event_type="email",
            source="ABC Auctions",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            content={
                "from": "info@abcauctions.com",
                "subject": "Lot 42 - Equipment pickup Friday",
                "body": "We have lot 42 at 1200 Harmon Road. Equipment requires rigging. Can you pick up Friday?",
                "lot": "42",
                "location": "1200 Harmon Road",
                "date": "Friday",
            },
            importance=9,
        ),
        Event(
            event_type="market_data",
            source="Market Scanner",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            content={
                "symbol": "QQQ",
                "signal": "BUY",
                "strategy": "Mean Reversion",
                "entry": 387.50,
                "stop": 385.20,
                "target": 392.30,
                "confidence": 0.68,
            },
            importance=7,
        ),
        Event(
            event_type="health_alert",
            source="System Monitor",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            content={
                "severity": "NORMAL",
                "message": "Daily health check passed. All systems online.",
            },
            importance=3,
        ),
    ]

    all_actions = []

    # Process events
    for event in events:
        print(f"\n{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        actions = processor.process(event)

        # Check permissions and execute
        for action in actions:
            approved = enforcer.evaluate(action)
            if approved:
                enforcer.execute(action)

        all_actions.extend(actions)
        time.sleep(1)

    # Show dashboard
    print_dashboard(memory, processor, all_actions)

    # Show trading strategies
    show_trading_strategy_example()

    # Show alerts
    show_alert_examples()

    # Memory inspection
    print(f"\n{Back.CYAN}{Fore.WHITE}{'='*70}{Style.RESET_ALL}")
    print(f"{Back.CYAN}{Fore.WHITE}{'NEXUS MEMORY SNAPSHOT':^70}{Style.RESET_ALL}")
    print(f"{Back.CYAN}{Fore.WHITE}{'='*70}{Style.RESET_ALL}")

    context = memory.get_context()

    print(f"\n{Fore.CYAN}PERMANENT FACTS{Style.RESET_ALL}")
    print(f"  Business: {context['facts']['business_name']}")
    print(f"  Type: {context['facts']['business_type']}")
    print(f"  Customers: {len(context['facts']['customers'])}")
    print(f"  Vendors: {len(context['facts']['vendors'])}")

    print(f"\n{Fore.CYAN}OPERATIONAL STATE{Style.RESET_ALL}")
    for key, val in context['operations'].items():
        print(f"  {key}: {val}")

    print(f"\n{Fore.CYAN}DECISION LOG (recent){Style.RESET_ALL}")
    for decision in context['decisions']:
        print(f"  [{decision['timestamp']}] {decision['decision']}")
        print(f"    → {decision['action_taken']}")

    print(f"\n{Back.CYAN}{Fore.WHITE}{'='*70}{Style.RESET_ALL}\n")

    print(f"{Fore.GREEN}DEMO COMPLETE{Style.RESET_ALL}\n")

    print(f"""
{Fore.YELLOW}KEY TAKEAWAYS:{Style.RESET_ALL}

1. {Fore.CYAN}EVENT LOOP{Style.RESET_ALL}
   ✓ System continuously monitors: emails, market data, alerts, calendars
   ✓ Each event triggers analysis → classification → decision

2. {Fore.CYAN}PERMISSION SYSTEM{Style.RESET_ALL}
   ✓ Level 0: Read-only (market analysis, monitoring)
   ✓ Level 1: Recommendations only
   ✓ Level 2: Auto-approved (low-risk tasks)
   ✓ Level 3: Business actions (needs approval first)
   ✓ Level 4: Financial actions (explicit approval required)
   ✓ Level 5: Locked forever (security-critical)

3. {Fore.CYAN}BUSINESS AUTOMATION{Style.RESET_ALL}
   ✓ Email → automatically creates jobs, schedules, reminders
   ✓ Invoice tracking → automatic payment reminders
   ✓ Task management → prioritizes what you need to do

4. {Fore.CYAN}TRADING ENGINE{Style.RESET_ALL}
   ✓ Multiple strategies (Trend, Momentum, Mean Reversion, Breakout, etc.)
   ✓ All backtested before going live
   ✓ Paper trading for validation
   ✓ Risk management enforced on every trade

5. {Fore.CYAN}INTEGRATIONS{Style.RESET_ALL}
   ✓ Slack: operational command center
   ✓ Discord: real-time trading updates
   ✓ Email: business/financial alerts
   ✓ Dashboard: complete history + status

6. {Fore.CYAN}MEMORY & CONTEXT{Style.RESET_ALL}
   ✓ Permanent facts (customers, vendors, locations)
   ✓ Operational state (current jobs, money, positions)
   ✓ Decision history (why actions were taken)
   ✓ System understands context, not just reacting

{Fore.GREEN}This is what the REAL system will do, 24/7, automatically.{Style.RESET_ALL}
{Fore.YELLOW}Ready to build it for real?{Style.RESET_ALL}
""")


if __name__ == "__main__":
    main()
