# RICK Automated Trading Environment - Quick Start Guide
## Paper Trading Setup with Live Narration Viewer

This guide helps you set up and run the RICK automated trading system in **PAPER TRADING MODE ONLY** with real-time monitoring.

---

## 🔒 Safety First

**IMPORTANT:** This system is configured for **PAPER TRADING ONLY**:
- ✅ OANDA Practice Account (fake money)
- ✅ Coinbase Sandbox (simulated trading)
- ✅ Interactive Brokers Paper Account (paper trading)
- ❌ NO real money at risk
- ❌ NO live trading enabled

---

## 📋 Prerequisites

### Required Software
```bash
# Python 3.8+
python3 --version

# jq (JSON processor for narration viewer)
sudo apt-get install jq

# Required Python packages
pip install -r requirements.txt
```

### Environment Configuration
The system uses `master_paper_env.env` for all paper trading configurations:
- **OANDA:** Practice account (101-001-31210531-002)
- **Coinbase:** Sandbox environment
- **Interactive Brokers:** Paper account (DUK880040) on port 7497

---

## 🚀 Quick Start

### Option 1: View Live Narration Only
If the trading system is already running and you just want to monitor it:

```bash
# From project root
./view_live_narration.sh

# OR from util directory
cd util
./plain_english_narration.sh
```

This will display:
- Last 10 trading events
- Real-time streaming of new events
- Color-coded event types (signals, trades, analysis, errors)

### Option 2: Start Trading System + Narration
```bash
# Start paper trading
./start_paper.sh

# In another terminal, start narration viewer
./view_live_narration.sh
```

---

## 🎯 What You'll See in the Narration Viewer

The narration viewer displays trading events in real-time with color coding:

| Event Type | Color | Description |
|------------|-------|-------------|
| 🔍 SCAN_START | Cyan | Market scanning initiated |
| 📊 SIGNAL_GENERATED | Yellow | Trading signal detected |
| ❌ SIGNAL_REJECTED | Red | Signal rejected (risk check failed) |
| 🟢 TRADE_OPENED | Green | New position opened |
| ✅ TRADE_CLOSED (Win) | Green | Position closed with profit |
| ❌ TRADE_CLOSED (Loss) | Red | Position closed with loss |
| 🐝 HIVE_ANALYSIS | Cyan | Multi-strategy consensus |
| 🛡️ RISK_CHECK | Magenta | Risk validation performed |
| 🚀 SESSION_START | Green | Trading session started |
| 🏁 SESSION_END | Cyan | Trading session ended |
| ⚠️ ERROR | Red | Error occurred |

---

## 📊 Broker Configuration

### OANDA (Forex Paper Trading)
- **Account:** Practice account 101-001-31210531-002
- **URL:** https://api-fxpractice.oanda.com
- **Pairs:** EUR_USD, GBP_USD, USD_JPY, and more
- **Capital:** $2,000 (paper money)

### Coinbase (Crypto Sandbox)
- **Environment:** Sandbox (simulated trading)
- **URL:** https://public-sandbox.exchange.coinbase.com
- **Pairs:** BTC-USD, ETH-USD, ADA-USD, and more
- **Capital:** $2,000 (paper money)

### Interactive Brokers (Paper Account)
- **Account:** DUK880040
- **Port:** 7497 (paper trading port)
- **Note:** Port 7496 is LIVE trading (NOT used)
- **Gateway:** IB Gateway or TWS must be running
- **Capital:** $2,000 (paper money)

---

## 🛠️ Configuration Files

### Primary Configuration
- `master_paper_env.env` - Main paper trading environment
  - All broker credentials
  - Safety settings (paper-only mode)
  - Risk management parameters

### Key Safety Settings
```bash
TRADING_ENVIRONMENT=sandbox
TRADING_MODE=paper
SAFETY_PAPER_ONLY=true
PREVENT_LIVE_TRADING=true
```

---

## 📝 Monitoring & Logs

### Live Narration
```bash
./view_live_narration.sh
```

### Log Files
- `narration.jsonl` - All trading events in JSON format
- `logs/trades.jsonl` - Trade history
- `logs/pnl.jsonl` - Profit & loss tracking
- `logs/errors.log` - Error messages

### Manual Log Viewing
```bash
# View raw narration log
tail -f narration.jsonl | jq .

# View recent trades
tail -20 logs/trades.jsonl | jq .
```

---

## 🔧 Troubleshooting

### Narration Viewer Not Starting
```bash
# Check if jq is installed
which jq

# Install jq if missing
sudo apt-get install jq

# Check if narration log exists
ls -la narration.jsonl
```

### No Trading Events Appearing
- Verify trading system is running
- Check if `narration.jsonl` file is being updated:
  ```bash
  ls -lh narration.jsonl
  tail -1 narration.jsonl
  ```

### IB Gateway Connection Issues
- Ensure IB Gateway or TWS is running
- Verify paper trading mode (port 7497)
- Check IB Gateway is accepting API connections
- Verify account number: DUK880040

### OANDA/Coinbase Connection Issues
- Check internet connection
- Verify API credentials in `master_paper_env.env`
- Check API endpoints are accessible:
  ```bash
  curl https://api-fxpractice.oanda.com/v3/accounts
  curl https://public-sandbox.exchange.coinbase.com/products
  ```

---

## ⚠️ Important Notes

1. **Paper Trading Only:** This system is configured for paper/sandbox trading ONLY
2. **No Real Money:** All configured accounts use fake money for testing
3. **Port Safety:** IB Gateway port 7497 = paper, 7496 = live (we use 7497 ONLY)
4. **Ghost Trading:** No ghost/simulated trades - all trading through real broker APIs in paper mode
5. **Capital Limits:** Each broker limited to $2,000 paper capital

---

## 🎓 Learning & Development

### Understanding the Narration
The narration viewer helps you:
- See what the trading system is thinking
- Understand why trades are opened/rejected
- Monitor risk management in action
- Learn trading strategies being used

### Customizing Event Display
Edit `util/plain_english_narration.sh` to:
- Add new event types
- Change color schemes
- Modify display formats
- Add custom filtering

---

## 📞 Support & Documentation

### Quick Links
- System architecture: `system_architecture.png`
- Monitor script: `monitor_narration.sh` (alternative viewer)
- Paper trading script: `start_paper.sh`

### Additional Documentation
- `PAPER_README.md` - Paper trading basics
- `MONITORING_QUICK_REFERENCE.md` - Monitoring guide
- `FASTEST_PATH_TO_LIVE.md` - Live trading guide (future use)

---

## ✅ Verification Checklist

Before trading:
- [ ] `master_paper_env.env` loaded
- [ ] TRADING_ENVIRONMENT=sandbox confirmed
- [ ] All three brokers configured (OANDA, Coinbase, IBKR)
- [ ] jq installed for narration viewer
- [ ] IB Gateway running (if using IBKR)
- [ ] Narration viewer accessible

---

**Remember:** This is a paper trading system. No real money is at risk. Use it to learn, test strategies, and build confidence before considering live trading.

Last updated: 2025-11-20
PIN: 841921
