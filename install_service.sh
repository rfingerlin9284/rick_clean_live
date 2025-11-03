#!/bin/bash
# Install RICK Trading System as a systemd service for auto-restart

echo "════════════════════════════════════════════════════════════════"
echo "🔧 RICK Trading System - Service Installation"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "❌ Please do NOT run as root. Run as your normal user."
   echo "   The script will ask for sudo password when needed."
   exit 1
fi

echo "This will install RICK as a systemd service that:"
echo "  ✅ Starts automatically on boot"
echo "  ✅ Restarts automatically if it crashes"
echo "  ✅ Sends alerts on startup/shutdown/restart"
echo "  ✅ Runs continuously in the background"
echo ""

read -p "Continue with installation? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Installation cancelled"
    exit 0
fi

echo ""
echo "📋 Step 1: Copying service file..."
sudo cp rick-trading.service /etc/systemd/system/
echo "✅ Service file copied"

echo ""
echo "📋 Step 2: Reloading systemd..."
sudo systemctl daemon-reload
echo "✅ Systemd reloaded"

echo ""
echo "📋 Step 3: Service commands available:"
echo ""
echo "  Start service:    sudo systemctl start rick-trading"
echo "  Stop service:     sudo systemctl stop rick-trading"
echo "  Check status:     sudo systemctl status rick-trading"
echo "  Enable on boot:   sudo systemctl enable rick-trading"
echo "  Disable on boot:  sudo systemctl disable rick-trading"
echo "  View logs:        sudo journalctl -u rick-trading -f"
echo ""

read -p "Enable auto-start on boot? (yes/no): " enable_boot

if [ "$enable_boot" = "yes" ]; then
    echo ""
    echo "📋 Step 4: Enabling auto-start on boot..."
    sudo systemctl enable rick-trading
    echo "✅ Service will start automatically on boot"
else
    echo ""
    echo "⚠️  Auto-start on boot NOT enabled"
    echo "   You can enable it later with: sudo systemctl enable rick-trading"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Installation Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Configure alerts in env_new.env:"
echo "   ALERT_WEBHOOK_ENABLED=true"
echo "   ALERT_WEBHOOK_URL=https://your-webhook-url"
echo "   ALERT_TELEGRAM_ENABLED=true"
echo "   ALERT_TELEGRAM_BOT_TOKEN=your_bot_token"
echo "   ALERT_TELEGRAM_CHAT_ID=your_chat_id"
echo ""
echo "2. Test the service:"
echo "   sudo systemctl start rick-trading"
echo "   sudo systemctl status rick-trading"
echo ""
echo "3. Monitor live:"
echo "   ./start_monitor_tmux.sh"
echo ""
echo "════════════════════════════════════════════════════════════════"
