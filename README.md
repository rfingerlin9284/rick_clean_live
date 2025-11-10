🚀 RICK Trading System - Complete Activation Package

**Status:** Implementation Specifications Ready  
**Charter PIN:** 841921  

## 📦 What This Repository Provides

This repository contains **COMPLETE SPECIFICATIONS AND TOOLS** to implement the RICK trading system with:
- Foundation layer (Charter with PIN 841921)
- Hive gatekeeping system (4 validation gates)
- Logic layer (5-regime detection)
- Wolf Pack strategies (Bullish/Bearish/Sideways)
- Trading engines (Ghost/Canary)
- Risk management
- Broker integration (OANDA)

## 🚀 Quick Start

### 1. Read the Activation Package
```bash
cat README_ACTIVATION_PACKAGE.md
```

### 2. Read the Mega Prompt (Complete Specifications)
```bash
cat VSCODE_AGENT_MEGA_PROMPT_RICK_ACTIVATION.md
```

### 3. Run System Verification
```bash
bash scripts/verify_and_activate_all_systems.sh
```

### 4. Implement Components
Follow the specifications in the mega prompt to implement each component, OR copy from external source if available.

### 5. Activate System
Once verification passes (100%), activate paper trading:
```bash
python3 canary_trading_engine.py --continuous --duration 45
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **README_ACTIVATION_PACKAGE.md** | Executive summary - start here |
| **VSCODE_AGENT_MEGA_PROMPT_RICK_ACTIVATION.md** | Complete implementation specs |
| **SYSTEM_STATUS_AND_ACTIVATION_GUIDE.md** | Status tracking & checklists |
| **scripts/verify_and_activate_all_systems.sh** | Automated verification |

## 🔒 Charter Compliance (Non-Negotiable)

- ✅ Charter PIN: 841921
- ✅ Max Hold Time: 6 hours
- ✅ Min Risk/Reward: 3.2:1
- ✅ Timeframes: M15, M30, H1 only
- ✅ 4 Guardian Gates validate ALL trades

---

## Legacy Information

Legacy code and duplicate artifacts have been archived to `legacy_leftovers/` and `archives/` and are excluded from this git repo.


## 🎓 For Developers & Agents

### If you are a VSCode agent implementing this system:

1. **READ** `VSCODE_AGENT_MEGA_PROMPT_RICK_ACTIVATION.md` (complete specs)
2. **RUN** `bash scripts/verify_and_activate_all_systems.sh` (see what's needed)
3. **IMPLEMENT** components using specifications provided
4. **VERIFY** after each component (re-run verification script)
5. **INTEGRATE** following integration instructions in mega prompt
6. **ACTIVATE** only after 100% verification pass

**DO NOT SKIP STEPS. DO NOT BYPASS CHARTER VALIDATION.**

---

## Developer Quickstart (Original Instructions)

1. Create a python virtualenv and install deps:

```bash
./scripts/setup_dev.sh
source .venv/bin/activate
```

2. Copy env example and edit secrets:

```bash
cp env.example .env
# Edit .env to set any needed runtime and sandbox credentials
```

3. Run smoke checks and tests:

```bash
bash ./charter_check.sh
pytest -q
```

4. Run canary (stub):

```bash
./scripts/run_canary.sh
```

5. Promotion: use the GitHub Action `Promotion` (requires approval code).

Note: We run tests in two modes for comparison — once with no seed and once with `UNIBOT_SEED` set (see `scripts/test_both_modes.sh`). This helps detect issues that only appear under different randomness.


## Legacy READMEs moved (updated 20250922T153040)

No README files were moved.
