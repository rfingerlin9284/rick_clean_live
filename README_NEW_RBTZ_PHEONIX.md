# New_rbtz_pheonix
Newest most advanced tuned prototype based off the rbotzilla_pheonix repo.

## Current Status

This repository **currently only contains documentation and project setup guidance**.

What is already completed in this repository:
- Basic GitHub repository creation
- README instructions for linking the project folder to a local computer

What is **not** completed in this repository yet:
- No Coinbase Advanced Trade implementation
- No OANDA v20 implementation
- No shared market data or signal engine
- No headless bot runner or deployment scripts
- No test suite, CI workflow, or build pipeline
- No news-scanning or confidence-scoring background service

If the goal is a headless trading system that can trade Coinbase and OANDA at the same time, that work still needs to be built.

## Recommended Architecture

For a system that trades both Coinbase and OANDA, the best approach is usually:

1. **Keep execution adapters separate**
   - `coinbase` connector for crypto trading
   - `oanda` connector for FX / CFDs / metals trading
2. **Share one common research and signal layer**
   - market data normalization
   - cross-market feature generation
   - news and event scoring
   - confidence scoring and risk rules
3. **Share one portfolio/risk layer**
   - total exposure limits
   - correlation limits
   - position sizing
   - kill-switch / safety rules

This is safer than forcing both brokers into one monolithic execution engine. In practice, they should be **separate brokers with shared intelligence**.

## Should Coinbase and OANDA Stay Separate?

**Execution:** yes, keep them separate.  
**Signals, research, and risk context:** no, those should be shared.

That gives you:
- cleaner broker-specific order handling
- easier debugging
- safer credential separation
- one place to compute intermarket signals
- one place to score trade confidence across all connected markets

## What Needs To Be Addressed To Reach A Headless Multi-Broker System

### Phase 1: Foundation
- Add a real project structure
- Add environment variable support for secrets
- Add a headless runtime entrypoint
- Add logging and persistent state storage
- Add tests for core signal and broker code

### Phase 2: Broker Connectivity
- Implement Coinbase Advanced Trade authentication and order flows
- Implement OANDA v20 authentication and order flows
- Add account sync, open order sync, and position sync
- Add retry, reconnect, and error handling

### Phase 3: Shared Intelligence
- Build a normalized market data model across crypto, FX, indices, and metals
- Add cross-market feature generation
- Add a confidence engine that blends technical, macro, and news inputs
- Add market regime detection

### Phase 4: Risk Controls
- Per-broker risk limits
- Global portfolio risk limits
- Correlation and concentration limits
- Max drawdown / kill switch controls

### Phase 5: Automation
- Background news scanner
- Background market scanner
- Headless scheduler / daemon
- Monitoring, alerts, and audit logs

## Cross-Market Research Notes

Cross-market information can be useful, but it should be used as a **feature** or **context signal**, not as a hard rule.

Examples of useful relationships:
- **Gold vs USD:** gold often strengthens when the US dollar weakens
- **BTC vs risk sentiment:** bitcoin can trade with or against equities depending on the regime
- **USD strength vs FX pairs:** a stronger dollar can affect EUR/USD, GBP/USD, and other majors
- **Volatility spillovers:** stress in one market can spill into crypto, FX, equities, and metals

Important caution:
- these relationships change over time
- they can reverse during stress events
- they should be measured with rolling windows, regime filters, and confidence scores

Examples of better features:
- rolling BTC / gold correlation
- rolling BTC / Nasdaq correlation
- gold momentum
- DXY trend
- VIX or volatility proxy
- macro-news event intensity
- spread and relative-strength signals

## News And Background Scanning Features

The requested background feature of scanning markets and news outlets to score confidence is a reasonable design goal.

A practical first version would:
- poll major market calendars and broker-supported instruments
- track major scheduled macro events
- ingest trusted news headlines
- classify each item by affected market, direction, and confidence
- combine that with technical signals before allowing a trade

That is a better design than letting headlines place trades directly.

## Coinbase Advanced Trade Notes

Coinbase Advanced Trade is suitable for a headless bot, but it requires:
- secure API key handling
- short-lived authenticated request signing
- careful websocket reconnect handling
- order, fill, and balance reconciliation

Start with:
- account read access
- market data
- paper-safe validation logic
- then live order routing with strict limits

## OANDA Notes

OANDA v20 already supports the main workflows needed for automation:
- live and practice environments
- market data and streaming prices
- historical candle data
- market, limit, stop, and trailing-stop order support
- account, trade, and position management

That makes OANDA a good early target for building and validating the headless framework in practice mode first.

## Minimal Build Recommendation

To keep the first build practical, start with:

1. one headless service
2. one shared signal engine
3. two broker adapters:
   - Coinbase Advanced Trade
   - OANDA v20
4. paper/practice mode first
5. one small cross-market feature set:
   - BTC momentum
   - gold momentum
   - DXY trend
   - rolling BTC/gold correlation
   - scheduled macro-event risk flag

That is enough to prove the architecture before adding more strategies.

## Linking This Project to Your Local Computer

Follow these steps to clone and connect this repository to a folder on your local machine:

### Prerequisites
- [Git](https://git-scm.com/downloads) installed on your computer
- A [GitHub account](https://github.com) with access to this repository

### Clone the Repository

1. Open a terminal (Command Prompt, PowerShell, or a Unix shell).
2. Navigate to the folder where you want to store the project:
   ```bash
   cd /path/to/your/desired/folder
   ```
3. Clone the repository:
   ```bash
   git clone https://github.com/rfingerlin9284/New_rbtz_pheonix.git
   ```
4. Enter the newly created project folder:
   ```bash
   cd New_rbtz_pheonix
   ```

Your local folder is now linked to this GitHub repository.

### Keeping Your Local Folder in Sync

- **Pull the latest changes** from GitHub at any time:
  ```bash
  git pull origin main
  ```
- **Push your local changes** back to GitHub:
  ```bash
  git add .
  git commit -m "Your commit message"
  git push origin main
  ```

### Setting a Remote (if you already have a local folder)

If you already have a local folder with files and want to link it to this repository instead of cloning:

```bash
cd /path/to/your/existing/folder
git init
git remote add origin https://github.com/rfingerlin9284/New_rbtz_pheonix.git
git pull origin main
```

## Simple Next Step

If you want this repository to move beyond documentation, the next concrete milestone should be:

- create the Python project structure
- add configuration loading from environment variables
- add a headless runner
- scaffold Coinbase and OANDA connector modules
- implement paper/practice-mode account and market data checks first

That would turn this repository from a linked folder into the beginning of the actual trading system.
