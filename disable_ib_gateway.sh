#!/bin/bash
# Disable IB Gateway Integration (Keep for Future)
# This script comments out all IB Gateway references
# PIN: 841921 | Date: 2025-10-14

echo "🔧 Disabling IB Gateway Integration"
echo "======================================"
echo ""
echo "📌 This will:"
echo "   ✅ Comment out IB Gateway configuration"
echo "   ✅ Rename IB test files with .DISABLED extension"
echo "   ✅ Update documentation to show IB as future feature"
echo "   ✅ Keep all code intact for later reactivation"
echo ""
echo "🎯 System will use: OANDA (Forex) + Coinbase (Crypto) ONLY"
echo ""

# Confirmation
read -p "Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 1
fi

echo ""
echo "🔄 Starting IB Gateway disable process..."
echo ""

# 1. Comment out IB Gateway in env_new2.env
echo "📝 Step 1: Updating env_new2.env..."
cp env_new2.env env_new2.env.backup_$(date +%Y%m%d_%H%M%S)

cat >> env_new2.env << 'EOF'

# ============================================================================
# INTERACTIVE BROKERS GATEWAY - DISABLED (FUTURE USE)
# ============================================================================
# NOTE: IB Gateway integration is prepared but not currently active
# Current system uses: OANDA (Forex) + Coinbase (Crypto)
# To re-enable: Uncomment lines below and run ./enable_ib_gateway.sh

# IB_GATEWAY_HOST=172.25.80.1
# IB_GATEWAY_PORT=7497
# IB_ACCOUNT_ID=DU6880040
# IB_CLIENT_ID=1
# IB_TRADING_MODE=paper
# IB_MAX_CAPITAL_USD=2000.00
# IB_LIVE_GATEWAY_PORT=4001
# IB_LIVE_ACCOUNT_ID=your_live_account_id_here

EOF

# Remove old IB config from env_new2.env
sed -i '/^IB_GATEWAY_HOST=/d' env_new2.env
sed -i '/^IB_GATEWAY_PORT=/d' env_new2.env
sed -i '/^IB_ACCOUNT_ID=/d' env_new2.env
sed -i '/^IB_CLIENT_ID=/d' env_new2.env
sed -i '/^IB_TRADING_MODE=/d' env_new2.env
sed -i '/^IB_MAX_CAPITAL_USD=/d' env_new2.env
sed -i '/^IB_LIVE_GATEWAY_PORT=/d' env_new2.env
sed -i '/^IB_LIVE_ACCOUNT_ID=/d' env_new2.env

echo "   ✅ env_new2.env updated (backup created)"

# 2. Rename IB test files
echo ""
echo "📝 Step 2: Disabling IB test files..."

IB_TEST_FILES=(
    "test_correct_symbols.py"
    "test_forex_crypto_data.py"
    "test_live_market_data.py"
    "test_market_data_permissions.py"
    "check_ib_balance.py"
    "check_ib_gateway.sh"
    "diagnose_ib_connection.sh"
    "discover_available_data.py"
    "market_data_diagnostic.py"
    "install_ib_gateway.sh"
    "install_ib_gateway_improved.sh"
    "setup_wsl_ibgateway.sh"
)

for file in "${IB_TEST_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "${file}.DISABLED"
        echo "   ✅ Disabled: $file"
    fi
done

# 3. Move IB documentation
echo ""
echo "📝 Step 3: Archiving IB Gateway documentation..."

mkdir -p docs/future_features/ib_gateway

IB_DOCS=(
    "IB_GATEWAY_SETUP_COMPLETE.md"
    "IB_GATEWAY_API_ISSUE.md"
    "ib_market_data_setup.txt"
    "fix_ib_api.txt"
)

for doc in "${IB_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        mv "$doc" "docs/future_features/ib_gateway/"
        echo "   ✅ Archived: $doc"
    fi
done

# 4. Update CAPITAL_ALLOCATION_ALIGNED.md
echo ""
echo "📝 Step 4: Updating capital allocation documentation..."

cat > CAPITAL_ALLOCATION_ALIGNED.md << 'EOF'
# 💰 CAPITAL ALLOCATION SUMMARY - OANDA + Coinbase

**Date**: 2025-10-14  
**Total Capital**: $4,000 ($2,000 per broker)  
**PIN**: 841921  
**Status**: IB Gateway DISABLED (Future Feature)

---

## 📊 ACTIVE BROKER ACCOUNTS

### **1. OANDA (Forex)**
- **Account**: 101-001-31210531-002 (Practice)
- **Capital**: $2,000.00
- **Status**: ✅ ACTIVE
- **Purpose**: Forex pairs (EUR/USD, GBP/USD, USD/JPY, etc.)

### **2. Coinbase Advanced Trade (Crypto)**
- **Account**: Sandbox
- **Capital**: $2,000.00
- **Status**: ✅ ACTIVE
- **Purpose**: Spot crypto (BTC-USD, ETH-USD, etc.)

---

## 🔮 FUTURE EXPANSION (DISABLED)

### **3. Interactive Brokers (Multi-Asset) - PREPARED BUT INACTIVE**
- **Account**: DU6880040 (Paper Trading)
- **Actual Balance**: $10,750.93
- **Capital Limit**: $2,000.00 (when enabled)
- **Status**: ⏸️ DISABLED - Code ready, not currently active
- **Purpose**: Stocks, Crypto Futures, Forex (future expansion)
- **Re-enable**: Run `./enable_ib_gateway.sh` when ready

**Why Disabled Now:**
- Focus on Forex + Crypto mastery first
- OANDA + Coinbase provide sufficient market coverage
- IB adds complexity without immediate need
- Code preserved for easy future activation

---

## 🎯 CURRENT CAPITAL STRATEGY

### **Active Allocation:**
```
OANDA:    $2,000 (50%)  → Forex
Coinbase: $2,000 (50%)  → Crypto Spot
────────────────────────
TOTAL:    $4,000 (100%)
```

### **Future Allocation (When IB Enabled):**
```
OANDA:    $2,000 (33%)  → Forex
Coinbase: $2,000 (33%)  → Crypto Spot
IB:       $2,000 (33%)  → Multi-Asset
────────────────────────
TOTAL:    $6,000 (100%)
```

---

## 📋 POSITION SIZING EXAMPLES (CURRENT)

### **Forex Trade (OANDA)**
```
Capital: $2,000
Risk per trade: 2% = $40
EUR/USD @ 1.0850
Stop loss: 50 pips
Position size: 8,000 units ($40 / 0.0050 = 8,000)
Notional: $8,680 (with leverage)
```

### **Crypto Spot (Coinbase)**
```
Capital: $2,000
Risk per trade: 2% = $40
BTC @ $42,000
Stop loss: 2% = $840
Position size: 0.047 BTC ($40 / $840 = 0.047)
Notional: $1,974
```

---

## 🔧 VERIFICATION COMMANDS

### **Check OANDA Status**
```bash
python3 test_oanda_paper.py
```

### **Check Coinbase Status**
```bash
python3 -c "
from brokers.coinbase_connector import CoinbaseConnector
cb = CoinbaseConnector(pin=841921, environment='sandbox')
print(cb.get_account_summary())
"
```

### **Check System Mode**
```bash
python3 -c "
from util.mode_manager import get_mode_info
print(get_mode_info())
"
```

---

## ✅ CURRENT SYSTEM STATUS

- [x] OANDA configured with $2k capital
- [x] Coinbase configured with $2k allocation
- [x] Capital allocation documented
- [x] Position sizing examples provided
- [x] IB Gateway code preserved for future
- [ ] IB Gateway active (DISABLED - future feature)

---

**Current Status**: ✅ Two-broker system operational!  
**Next Milestone**: Master Forex + Crypto before adding third broker.  
**Future Expansion**: IB Gateway ready when needed.
EOF

echo "   ✅ Updated CAPITAL_ALLOCATION_ALIGNED.md"

# 5. Create IB re-enable script for future
echo ""
echo "📝 Step 5: Creating re-enable script for future..."

cat > enable_ib_gateway.sh << 'ENABLE_SCRIPT'
#!/bin/bash
# Re-enable IB Gateway Integration
# Run this script when ready to add IB Gateway support
# PIN: 841921

echo "🔌 Re-enabling IB Gateway Integration"
echo "======================================"
echo ""
echo "⚠️  WARNING: This will:"
echo "   • Uncomment IB configuration in env_new2.env"
echo "   • Restore IB test files"
echo "   • Update capital allocation to 3-broker system"
echo ""

read -p "Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 1
fi

# Uncomment IB config
sed -i 's/# IB_GATEWAY_HOST=/IB_GATEWAY_HOST=/g' env_new2.env
sed -i 's/# IB_GATEWAY_PORT=/IB_GATEWAY_PORT=/g' env_new2.env
sed -i 's/# IB_ACCOUNT_ID=/IB_ACCOUNT_ID=/g' env_new2.env
sed -i 's/# IB_CLIENT_ID=/IB_CLIENT_ID=/g' env_new2.env
sed -i 's/# IB_TRADING_MODE=/IB_TRADING_MODE=/g' env_new2.env
sed -i 's/# IB_MAX_CAPITAL_USD=/IB_MAX_CAPITAL_USD=/g' env_new2.env

# Restore test files
for file in *.DISABLED; do
    if [ -f "$file" ]; then
        mv "$file" "${file%.DISABLED}"
    fi
done

echo ""
echo "✅ IB Gateway integration re-enabled!"
echo "📋 Next steps:"
echo "   1. Start IB Gateway/TWS"
echo "   2. Run: python3 check_ib_balance.py"
echo "   3. Test: python3 brokers/ib_connector.py"
ENABLE_SCRIPT

chmod +x enable_ib_gateway.sh
echo "   ✅ Created enable_ib_gateway.sh for future use"

# 6. Update README
echo ""
echo "📝 Step 6: Updating system documentation..."

cat >> README_COMPLETE_SNAPSHOT.md << 'EOF'

---

## 🔌 BROKER CONFIGURATION UPDATE (2025-10-14)

### Active Brokers (2):
- ✅ **OANDA** - Forex trading ($2,000 capital)
- ✅ **Coinbase** - Crypto spot trading ($2,000 capital)

### Prepared But Inactive (1):
- ⏸️ **Interactive Brokers** - Multi-asset trading
  - Code: `brokers/ib_connector.py` (fully functional)
  - Status: DISABLED for system focus
  - Re-enable: `./enable_ib_gateway.sh`
  - Documentation: `docs/future_features/ib_gateway/`

**Rationale:** Focus on mastering Forex + Crypto with 2 brokers before expanding to 3-broker system. IB Gateway adds stocks/futures capability but increases operational complexity.

EOF

echo "   ✅ Updated README_COMPLETE_SNAPSHOT.md"

# 7. Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ IB GATEWAY SUCCESSFULLY DISABLED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Current System Configuration:"
echo "   ✅ OANDA (Forex) - $2,000"
echo "   ✅ Coinbase (Crypto) - $2,000"
echo "   ⏸️ IB Gateway (Future) - Code preserved"
echo ""
echo "📁 Changes Made:"
echo "   ✅ env_new2.env - IB config commented out"
echo "   ✅ Test files - Renamed to .DISABLED"
echo "   ✅ Documentation - Archived to docs/future_features/"
echo "   ✅ Capital allocation - Updated to 2-broker system"
echo "   ✅ Re-enable script - Created for future use"
echo ""
echo "🎯 To Re-enable IB Gateway Later:"
echo "   ./enable_ib_gateway.sh"
echo ""
echo "✅ System ready for Forex + Crypto focus!"
