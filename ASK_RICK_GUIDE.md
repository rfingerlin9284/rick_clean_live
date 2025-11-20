# 💬 Ask RICK - Plain English Interface Guide

## Overview

**Ask RICK** is a simple, no-code way to interact with your RICK trading system. Just ask questions in plain English and get answers back - no coding knowledge required!

## Quick Start

### From VSCode (Recommended)
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Tasks: Run Task"
3. Select **"RICK: 💬 Ask RICK (Plain English Interface)"**

### From Terminal
```bash
./ask_rick.sh
```

## How It Works

Once you start the interface, you'll see:

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🤖 RICK PLAIN ENGLISH INTERFACE                           ║
║                    Ask Questions - Get Answers                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

RICK>
```

Just type your question and press Enter! The system will respond in plain English.

## What You Can Ask

### System Status Questions
- **"status"** - Show me the overall system status
- **"health"** - Is the system healthy?
- **"features"** - What features are available?

### Trading Questions
- **"trading"** - Is trading active right now?
- **"balance"** - What's my account balance?
- **"trades"** - Show me recent trades
- **"positions"** - What positions are currently open?
- **"activity"** - What's happening right now?

### Information Questions
- **"brokers"** - Which brokers am I using?
- **"config"** - Show me the system configuration
- **"logs"** - Show me recent activity logs
- **"signals"** - Show me recent trading signals
- **"errors"** - Are there any errors?

### Help Commands
- **"help"** - Show help menu
- **"menu"** - Show all available commands
- **"quit"** or **"exit"** - Leave the interface

## Example Conversations

### Example 1: Checking System Status
```
RICK> status

━━━ SYSTEM STATUS ━━━

✅ Trading Engine is RUNNING
✅ Narration System is ACTIVE
   Log size: 19M
⚠️  Dashboard is STOPPED
✅ Active Features: 77/95

RICK>
```

### Example 2: Checking Account Balance
```
RICK> balance

━━━ ACCOUNT BALANCES ━━━

📊 Paper Trading Accounts (Safe - Fake Money):

1. OANDA Practice Account
   Account: 101-001-31210531-002
   Type: Practice (Paper Trading)
   Status: Configured ✓

2. Coinbase Sandbox
   Type: Sandbox (Simulated)
   Status: Configured ✓

3. Interactive Brokers Paper
   Account: DUK880040
   Port: 7497 (Paper Trading)
   Status: Configured ✓

Note: All accounts are in PAPER TRADING mode.
No real money is being used.

RICK>
```

### Example 3: Checking Recent Activity
```
RICK> activity

━━━ RECENT ACTIVITY ━━━

Last 10 events:

[10:09:55] 🐝 HIVE_ANALYSIS - GBP_USD
[10:09:55] 🐝 HIVE_ANALYSIS - AUD_CHF
[10:10:00] 📊 SIGNAL_GENERATED - EUR_USD
[10:10:05] 🟢 TRADE_OPENED - EUR_USD
...

RICK>
```

### Example 4: Checking Which Brokers
```
RICK> brokers

━━━ CONFIGURED BROKERS ━━━

Your system is configured with 3 brokers in PAPER TRADING mode:

1. OANDA
   Type: Forex Trading
   Mode: Practice Account (Paper Trading)
   Account: 101-001-31210531-002
   Status: Safe - No Real Money ✓

2. Coinbase
   Type: Cryptocurrency Trading
   Mode: Sandbox (Simulated)
   Status: Safe - No Real Money ✓

3. Interactive Brokers (IBKR)
   Type: Stocks, Options, Futures
   Mode: Paper Account
   Account: DUK880040
   Status: Safe - No Real Money ✓

All brokers are in PAPER TRADING mode.
No real money is at risk.

RICK>
```

## Complete Command List

### System Status Commands
| Command | What It Does |
|---------|--------------|
| `status` | Shows overall system status |
| `health` | Performs system health check |
| `features` | Lists all 100+ available features |

### Trading Commands
| Command | What It Does |
|---------|--------------|
| `trading` | Shows if trading is active |
| `balance` | Shows account balances |
| `trades` | Shows recent trade history |
| `positions` | Shows currently open positions |
| `activity` | Shows recent trading activity |

### Information Commands
| Command | What It Does |
|---------|--------------|
| `brokers` | Lists configured brokers |
| `config` | Shows system configuration |
| `settings` | Shows system settings |
| `accounts` | Shows account information |

### Activity Commands
| Command | What It Does |
|---------|--------------|
| `logs` | Shows recent activity logs |
| `events` | Shows recent trading events |
| `signals` | Shows recent trading signals |
| `errors` | Shows any errors or warnings |

### Help Commands
| Command | What It Does |
|---------|--------------|
| `help` | Shows help menu |
| `menu` | Shows all available commands |
| `clear` | Clears the screen |
| `quit` | Exits the interface |
| `exit` | Exits the interface |

## Tips for Using Ask RICK

### You Don't Need to Type Exactly
The interface understands variations of commands:
- "status" or "what's the status" or "system status" all work
- "balance" or "what's my balance" or "account balance" all work
- Commands are case-insensitive (STATUS, status, Status all work)

### Commands Are Read-Only
- All commands are safe - they only **read** information
- Nothing you type can change the system or start/stop trading
- You can explore freely without worry

### Get Help Anytime
- Type `help` to see the help menu
- Type `menu` to see all available commands
- If you mistype something, RICK will tell you and suggest using `help`

### Exit When Done
- Type `quit` or `exit` to leave the interface
- Or just close the terminal window

## What Information You'll Get

### All Responses Are in Plain English
No technical jargon or code - just clear, easy-to-understand information like:
- "Trading Engine is RUNNING"
- "System Health: EXCELLENT (80%)"
- "All accounts are in PAPER TRADING mode"
- "No real money is being used"

### Color-Coded for Easy Reading
- ✅ Green: Good status, active features
- ⚠️  Yellow: Warnings, needs attention
- 📊 Blue: Information, data
- 🟢 Green circles: Trades opened
- ⚠️  Magenta: Errors or issues

## Frequently Asked Questions

### Q: Will this interface change anything in my system?
**A:** No! This interface is completely read-only. You can only view information, never change it.

### Q: Do I need to know how to code?
**A:** Not at all! Just type plain English questions and get plain English answers.

### Q: Can I break something by asking the wrong question?
**A:** No. All commands are safe. The worst that can happen is RICK won't understand and will ask you to try again.

### Q: What if I forget the commands?
**A:** Just type `help` or `menu` anytime to see what you can ask.

### Q: Is my money safe?
**A:** Yes! The entire system is in paper trading mode. No real money is being used at all.

### Q: How do I start trading?
**A:** This interface is for viewing information only. To start paper trading, exit this interface and run `./start_paper.sh` from the terminal.

### Q: Can I use this while trading is active?
**A:** Yes! You can use this interface anytime to check on your trading system, whether it's running or not.

## Troubleshooting

### Interface Won't Start
Make sure you're running it from the project directory:
```bash
cd /home/runner/work/rick_clean_live/rick_clean_live
./ask_rick.sh
```

### "Command Not Found" Error
The script might not be executable. Run:
```bash
chmod +x ask_rick.sh
./ask_rick.sh
```

### Want to Use in VSCode
Use the VSCode task instead:
1. `Ctrl+Shift+P`
2. "Tasks: Run Task"
3. "RICK: 💬 Ask RICK (Plain English Interface)"

## Advanced: Custom Questions

### Natural Language Variations
The interface understands many ways to ask the same question:

**For Status:**
- "status"
- "what's the status"
- "system status"
- "show status"

**For Trading:**
- "trading"
- "is trading active"
- "trading status"
- "am I trading"

**For Balance:**
- "balance"
- "what's my balance"
- "account balance"
- "show balance"

Feel free to ask naturally - RICK will try to understand!

## Related Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **Ask RICK** | Plain English Q&A | When you want quick info in simple language |
| **Persistent Monitor** | Comprehensive feature tracking | When you want to see all 100+ features at once |
| **Live Narration** | Real-time trading events | When you want to watch trades happen live |

## Summary

**Ask RICK is your no-code interface to the trading system:**
- ✅ Just type plain English questions
- ✅ Get plain English answers
- ✅ No coding knowledge needed
- ✅ Completely safe (read-only)
- ✅ Available anytime via VSCode or terminal
- ✅ Perfect for checking system status without technical details

Start exploring your trading system today - just type `help` and start asking questions!

---

**Quick Start:** Press `Ctrl+Shift+P` → "RICK: 💬 Ask RICK (Plain English Interface)"

**PIN: 841921** | **Last Updated: 2025-11-20**
