🚀 RICK Trading System - Complete Activation Package

**Status:** Implementation Specifications Ready + Frankenstein Assembly Guide
**Charter PIN:** 841921  
**NO TA-LIB:** Pure Python implementations provided

## 📦 What This Repository Provides

This repository contains **COMPLETE SPECIFICATIONS AND TOOLS** to implement the RICK trading system with:
- Foundation layer (Charter with PIN 841921)
- Hive gatekeeping system (4 validation gates)
- Logic layer (5-regime detection)
- Wolf Pack strategies (Bullish/Bearish/Sideways)
- Trading engines (Ghost/Canary)
- Risk management
- Broker integration (OANDA)

**NEW:** Frankenstein Assembly guide to combine your existing code from multiple repos - **NO TA-LIB required!**

## 🚀 Quick Start

### ⚡ FASTEST: Frankenstein Assembly from Your Existing Code (2-3 hours)

**If you have RICK code scattered across multiple repos:**

```bash
# 1. Find all your existing RICK code
bash scripts/inventory_existing_code.sh

# 2. Review what was found
cat code_inventory.txt

# 3. Read the Frankenstein assembly guide
cat VSCODE_AGENT_FRANKENSTEIN_ASSEMBLY.md

# 4. Give your VSCode agent the complete instructions
# Agent will combine files, remove TA-Lib, use pure Python

# 5. Verify (should show 100%)
bash scripts/verify_and_activate_all_systems.sh

# 6. Activate!
python3 canary_trading_engine.py --continuous --duration 45
```

**Key Benefits:**
- ✅ NO TA-LIB - Pure Python replacements provided
- ✅ Searches all your local repos
- ✅ Searches your GitHub repos
- ✅ Combines best versions
- ✅ Takes 2-3 hours (not weeks!)

---

### Alternative: Import Complete Files (5 minutes)

**If you already have the RICK files:**

```bash
# Use the import script
bash scripts/import_existing_files.sh /path/to/RICK_LIVE_CLEAN /path/to/R_H_UNI

# Verify (should show 100%)
bash scripts/verify_and_activate_all_systems.sh

# Activate!
python3 canary_trading_engine.py --continuous --duration 45
```

**That's it! Minutes, not weeks.**

---

### Alternative: Build from Specifications

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
