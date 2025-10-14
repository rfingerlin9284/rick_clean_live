.PHONY: help status clean stop install test
.PHONY: paper canary ghost live dashboard
.PHONY: paper-48h canary-session monitor logs

# Default target
.DEFAULT_GOAL := help

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
CYAN := \033[0;36m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "════════════════════════════════════════════════════════════════"
	@echo "🤖 RICK Trading System - Makefile Commands"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

status: ## Check current mode and running processes
	@echo "$(CYAN)═══════════════════════════════════════════════════════════════$(NC)"
	@echo "$(CYAN)🤖 RICK Trading System Status$(NC)"
	@echo "$(CYAN)═══════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(BOLD)Current Mode:$(NC)"
	@cat .upgrade_toggle 2>/dev/null || echo "  No mode set"
	@echo ""
	@echo "$(BOLD)Running Processes:$(NC)"
	@if [ -f .paper_trading.pid ] && ps -p $$(cat .paper_trading.pid 2>/dev/null) > /dev/null 2>&1; then \
		echo "  ✓ Paper Trading Engine (PID: $$(cat .paper_trading.pid))"; \
	else \
		echo "  ✗ Paper Trading Engine: NOT RUNNING"; \
	fi
	@if [ -f .dashboard_supervisor.pid ] && ps -p $$(cat .dashboard_supervisor.pid 2>/dev/null) > /dev/null 2>&1; then \
		echo "  ✓ Dashboard Supervisor (PID: $$(cat .dashboard_supervisor.pid))"; \
	else \
		echo "  ✗ Dashboard Supervisor: NOT RUNNING"; \
	fi
	@if ps aux | grep -E "python3.*dashboard/app.py" | grep -v grep > /dev/null; then \
		echo "  ✓ Dashboard Web Interface: RUNNING"; \
	else \
		echo "  ✗ Dashboard Web Interface: NOT RUNNING"; \
	fi
	@if ps aux | grep -E "python3.*rick_hive_mind" | grep -v grep > /dev/null; then \
		echo "  ✓ Rick Hive Mind: CONNECTED"; \
	else \
		echo "  ✗ Rick Hive Mind: NOT CONNECTED"; \
	fi
	@echo ""
	@echo "$(BOLD)Timezone & Session Info:$(NC)"
	@python3 util/timezone_manager.py
	@echo ""

install: ## Install Python dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	pip3 install -r requirements.txt

test: ## Run system tests
	@echo "$(GREEN)Running tests...$(NC)"
	python3 test_ghost_trading.py

##@ Trading Modes

paper: ## Start paper trading (dry-run mode, safe for testing)
	@echo "$(GREEN)Starting Paper Trading Mode (Dry-Run)...$(NC)"
	@bash start_paper.sh

paper-48h: ## Deploy paper trading for 48 hours (background mode)
	@echo "$(GREEN)════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)🚀 DEPLOYING PAPER TRADING FOR 48 HOURS$(NC)"
	@echo "$(GREEN)════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "This will:"
	@echo "  • Switch to CANARY mode"
	@echo "  • Start the trading engine in background"
	@echo "  • Run for 48 hours continuously"
	@echo "  • Log all activity to logs/"
	@echo ""
	@read -p "Proceed? (y/n): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo ""
	@echo "$(CYAN)Step 1: Switching to CANARY mode...$(NC)"
	@python3 -c "from util.mode_manager import switch_mode; switch_mode('CANARY')"
	@echo "$(GREEN)✓ Mode switched$(NC)"
	@echo ""
	@echo "$(CYAN)Step 2: Creating logs directory...$(NC)"
	@mkdir -p logs
	@echo "$(GREEN)✓ Logs directory ready$(NC)"
	@echo ""
	@echo "$(CYAN)Step 3: Starting trading engine in background...$(NC)"
	@nohup python3 canary_trading_engine.py > logs/paper_trading_48h.log 2>&1 & echo $$! > .paper_trading.pid
	@sleep 2
	@if ps -p $$(cat .paper_trading.pid 2>/dev/null) > /dev/null 2>&1; then \
		echo "$(GREEN)✓ Trading engine started (PID: $$(cat .paper_trading.pid))$(NC)"; \
	else \
		echo "$(RED)✗ Failed to start trading engine$(NC)"; \
		exit 1; \
	fi
	@echo ""
	@echo "$(GREEN)════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)🎉 PAPER TRADING DEPLOYED FOR 48 HOURS!$(NC)"
	@echo "$(GREEN)════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(CYAN)Monitor commands:$(NC)"
	@echo "  make monitor    - Watch live logs"
	@echo "  make status     - Check system status"
	@echo "  make logs       - View recent logs"
	@echo "  make stop       - Stop trading engine"
	@echo ""
	@echo "$(CYAN)Log file:$(NC) logs/paper_trading_48h.log"
	@echo "$(CYAN)PID file:$(NC) .paper_trading.pid"
	@echo ""

deploy-full-auto: ## Deploy FULL system automatically (for systemd service)
	@echo "$(GREEN)════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)🚀 AUTO-DEPLOYING RICK TRADING SYSTEM$(NC)"
	@echo "$(GREEN)════════════════════════════════════════════════════════════════$(NC)"
	@python3 -c "from util.mode_manager import switch_mode; switch_mode('CANARY')"
	@mkdir -p logs
	@nohup python3 canary_trading_engine.py > logs/paper_trading_48h.log 2>&1 & echo $$! > .paper_trading.pid
	@sleep 2
	@nohup python3 dashboard_supervisor.py > logs/dashboard_supervisor.log 2>&1 & echo $$! > .dashboard_supervisor.pid
	@sleep 3
	@echo "$(GREEN)✓ System deployed automatically$(NC)"

deploy-full: ## Deploy FULL system: paper trading + supervised dashboard (COMPLETE SOLUTION)
	@echo "$(GREEN)════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)🚀 DEPLOYING COMPLETE RICK TRADING SYSTEM$(NC)"
	@echo "$(GREEN)════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(BOLD)This will start:$(NC)"
	@echo "  ✓ Paper trading engine (48h CANARY mode)"
	@echo "  ✓ Web dashboard with auto-restart"
	@echo "  ✓ Rick Hive Mind collective"
	@echo "  ✓ Plain English narration logging"
	@echo "  ✓ 1-minute OpenAI rate limiting"
	@echo "  ✓ Automatic health monitoring"
	@echo ""
	@read -p "Deploy complete system? (y/n): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo ""
	@echo "$(CYAN)═══ Phase 1: Starting Paper Trading ═══$(NC)"
	@echo ""
	@python3 -c "from util.mode_manager import switch_mode; switch_mode('CANARY')"
	@mkdir -p logs
	@nohup python3 canary_trading_engine.py > logs/paper_trading_48h.log 2>&1 & echo $$! > .paper_trading.pid
	@sleep 2
	@if ps -p $$(cat .paper_trading.pid 2>/dev/null) > /dev/null 2>&1; then \
		echo "$(GREEN)✓ Trading engine running (PID: $$(cat .paper_trading.pid))$(NC)"; \
	else \
		echo "$(RED)✗ Failed to start trading engine$(NC)"; \
		exit 1; \
	fi
	@echo ""
	@echo "$(CYAN)═══ Phase 2: Starting Dashboard Supervisor ═══$(NC)"
	@echo ""
	@nohup python3 dashboard_supervisor.py > logs/dashboard_supervisor.log 2>&1 & echo $$! > .dashboard_supervisor.pid
	@sleep 3
	@if ps -p $$(cat .dashboard_supervisor.pid 2>/dev/null) > /dev/null 2>&1; then \
		echo "$(GREEN)✓ Dashboard supervisor running (PID: $$(cat .dashboard_supervisor.pid))$(NC)"; \
	else \
		echo "$(RED)✗ Failed to start dashboard supervisor$(NC)"; \
		exit 1; \
	fi
	@echo ""
	@echo "$(GREEN)════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)🎉 COMPLETE SYSTEM DEPLOYED SUCCESSFULLY!$(NC)"
	@echo "$(GREEN)════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(BOLD)System Status:$(NC)"
	@echo "  🤖 Trading Engine:    RUNNING (48h mode)"
	@echo "  📊 Dashboard:         RUNNING (supervised)"
	@echo "  🧠 Hive Mind:         CONNECTING"
	@echo "  📝 Narration:         ACTIVE"
	@echo ""
	@echo "$(BOLD)Access Points:$(NC)"
	@echo "  Dashboard:       http://localhost:5000"
	@echo "  Narration:       narration.jsonl"
	@echo "  Trading Logs:    logs/paper_trading_48h.log"
	@echo "  Supervisor Logs: logs/dashboard_supervisor.log"
	@echo ""
	@echo "$(BOLD)Management Commands:$(NC)"
	@echo "  make status      - Check all components"
	@echo "  make monitor     - Watch live logs"
	@echo "  make narration   - View narration feed"
	@echo "  make stop        - Stop everything"
	@echo ""
	@echo "$(YELLOW)System will run for 48 hours or until you stop it$(NC)"
	@echo ""

canary: ## Start CANARY mode (practice API, charter-compliant)
	@echo "$(GREEN)Starting CANARY Mode...$(NC)"
	@bash launch_canary.sh

canary-session: ## Quick CANARY validation session (45 minutes)
	@echo "$(GREEN)Starting CANARY validation session...$(NC)"
	@python3 -c "from util.mode_manager import switch_mode; switch_mode('CANARY')"
	@python3 canary_trading_engine.py 841921

ghost: ## Switch to GHOST mode
	@echo "$(YELLOW)Switching to GHOST mode...$(NC)"
	@python3 -c "from util.mode_manager import switch_mode; switch_mode('GHOST')"
	@cat .upgrade_toggle

live: ## Switch to LIVE mode (requires PIN)
	@echo "$(RED)⚠️  LIVE MODE - REAL MONEY TRADING$(NC)"
	@echo ""
	@read -p "Enter PIN (841921): " pin && \
	python3 -c "from util.mode_manager import switch_mode; switch_mode('LIVE', pin=$$pin)"
	@cat .upgrade_toggle

##@ Monitoring & Dashboard

dashboard: ## Start web dashboard (simple mode)
	@echo "$(GREEN)Starting dashboard...$(NC)"
	@python3 dashboard/app.py

dashboard-supervised: ## Start dashboard with auto-restart, narration & Hive Mind (RECOMMENDED)
	@echo "$(GREEN)════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)🤖 Starting RICK Dashboard Supervisor$(NC)"
	@echo "$(GREEN)════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "This will:"
	@echo "  ✓ Keep dashboard running continuously"
	@echo "  ✓ Auto-restart if it crashes"
	@echo "  ✓ Maintain Rick Hive Mind connection"
	@echo "  ✓ Log everything in plain English narration"
	@echo "  ✓ Apply 1-minute delays between OpenAI requests"
	@echo "  ✓ Auto-rotate large log files"
	@echo ""
	@python3 dashboard_supervisor.py

monitor: ## Monitor live trading logs (tail -f)
	@echo "$(CYAN)Monitoring logs (Ctrl+C to exit)...$(NC)"
	@if [ -f .paper_trading.pid ]; then \
		tail -f logs/paper_trading_48h.log; \
	elif [ -f logs/ghost_charter_compliant.log ]; then \
		tail -f logs/ghost_charter_compliant.log; \
	else \
		echo "$(YELLOW)No active log files found$(NC)"; \
		ls -lt logs/ | head -10; \
	fi

logs: ## Show last 50 lines of recent logs
	@echo "$(CYAN)Recent logs:$(NC)"
	@if [ -f .paper_trading.pid ]; then \
		tail -50 logs/paper_trading_48h.log; \
	elif [ -f logs/ghost_charter_compliant.log ]; then \
		tail -50 logs/ghost_charter_compliant.log; \
	else \
		echo "$(YELLOW)No active log files found$(NC)"; \
		echo "Available logs:"; \
		ls -lt logs/ | head -10; \
	fi

narration: ## View narration feed
	@echo "$(CYAN)Narration feed (last 20 entries):$(NC)"
	@if [ -f narration.jsonl ]; then \
		tail -20 narration.jsonl | python3 -c "import sys, json; [print(json.loads(line).get('text', line.strip())) for line in sys.stdin]"; \
	else \
		echo "No narration file found"; \
	fi

##@ Control & Maintenance

stop: ## Stop all trading engines
	@echo "$(YELLOW)Stopping all trading engines and dashboard...$(NC)"
	@if [ -f .paper_trading.pid ]; then \
		kill $$(cat .paper_trading.pid) 2>/dev/null || true; \
		rm -f .paper_trading.pid; \
		echo "$(GREEN)✓ Paper trading stopped$(NC)"; \
	fi
	@pkill -f "python3.*canary_trading_engine" || true
	@pkill -f "python3.*ghost_trading_engine" || true
	@pkill -f "python3.*live_ghost_engine" || true
	@pkill -f "python3.*dashboard/app.py" || true
	@pkill -f "python3.*dashboard_supervisor" || true
	@pkill -f "python3.*rick_hive_mind" || true
	@echo "$(GREEN)✓ All engines and dashboard stopped$(NC)"

restart-paper: stop paper-48h ## Stop and restart paper trading

clean: ## Clean logs and temporary files
	@echo "$(YELLOW)Cleaning temporary files...$(NC)"
	@rm -f .paper_trading.pid
	@rm -f __pycache__/*.pyc
	@echo "$(GREEN)✓ Cleaned$(NC)"

clean-logs: ## Clear all log files (keep directory)
	@echo "$(RED)⚠️  This will delete all log files!$(NC)"
	@read -p "Are you sure? (y/n): " confirm && [ "$$confirm" = "y" ] || exit 1
	@rm -f logs/*.log
	@> narration.jsonl
	@echo "$(GREEN)✓ Logs cleared$(NC)"

##@ Reports & Analysis

report: ## Show latest trading report
	@echo "$(CYAN)Latest Trading Report:$(NC)"
	@if [ -f canary_trading_report.json ]; then \
		cat canary_trading_report.json | python3 -m json.tool; \
	elif [ -f capital_summary.json ]; then \
		cat capital_summary.json | python3 -m json.tool; \
	else \
		echo "No reports found"; \
	fi

capital: ## Show capital summary
	@echo "$(CYAN)Capital Summary:$(NC)"
	@if [ -f capital_summary.json ]; then \
		cat capital_summary.json | python3 -m json.tool; \
	else \
		echo "No capital summary found"; \
	fi

timezone: ## Show timezone and session info
	@python3 util/timezone_manager.py

##@ Safety Checks

preflight: ## Run pre-flight safety checks
	@echo "$(CYAN)Running pre-flight checks...$(NC)"
	@bash live_preflight_check.sh

verify: ## Verify live safety settings
	@echo "$(CYAN)Verifying safety settings...$(NC)"
	@bash verify_live_safety.sh

##@ Rick Hive ML, Rbotzilla Automation, and Autonomy

##@ Safeguards

check-dashboard: ## Ensure the dashboard is running
	@echo "Checking if the dashboard is active..."
	@if ps aux | grep -E "python3.*dashboard/app.py" | grep -v grep > /dev/null; then \
		echo "✓ Dashboard Web Interface is RUNNING"; \
	else \
		echo "✗ Dashboard Web Interface is NOT RUNNING"; \
	fi

run-hive-ml: check-dashboard ## Run Rick Hive ML
	@echo "Running Rick Hive ML..."
	python3 hive/hive_mind_processor.py

run-rbotzilla: check-dashboard ## Run Rbotzilla Automation
	@echo "Running Rbotzilla Automation..."
	python3 rbotzilla/automation.py

enable-autonomy: check-dashboard ## Enable Rick Autonomy
	@echo "Enabling Rick Autonomy..."
	python3 hive/adaptive_rick.py
