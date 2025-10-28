#!/bin/bash
# === OPTIMIZED FULL PERMISSIONS FIXER FOR /home/ing/ AND ALL SUBFOLDERS ===
# Performance improvements: single-pass operations, batched exec, reduced redundancy

set -e

BASE_PATH="${1:-/home/ing}"

echo "🔓 FIXING ALL PERMISSIONS UNDER $BASE_PATH ..."

# 1. Take ownership once for everything
echo "📋 Taking ownership of all files and folders..."
sudo chown -R ing:ing "$BASE_PATH"

# 2. Set all permissions in two optimized passes (directories, then files)
echo "🛠️ Setting all permissions in optimized passes..."
find "$BASE_PATH" -type d -exec chmod 755 {} +
find "$BASE_PATH" -type f -exec chmod 644 {} +

# 3. Make all scripts and executables executable in one pass
echo "🚀 Setting executable permissions for scripts and programs..."
find "$BASE_PATH" -type f \( \
    -name "*.sh" \
    -o -name "*.py" \
    -o -name "*.pl" \
    -o -name "*.rb" \
    -o -name "autonomous_startup*" \
    -o -name "live_predict*" \
    -o -name "watchdog*" \
    -o -name "guardian*" \
\) -exec chmod 755 {} +

# 4. Fix Python virtual environment binaries in one pass
echo "🐍 Fixing Python virtual environments..."
find "$BASE_PATH" -type f \( \
    -path "*/.venv/bin/*" \
    -o -path "*/venv/bin/*" \
\) -exec chmod 755 {} +

# 5. Create critical directories if missing
echo "📁 Creating critical directories if missing..."
CRITICAL_DIRS=(
    "$BASE_PATH/RICK/Dev_unibot_v001"
    "$BASE_PATH/FOUR_horsemen/ALPHA_FOUR"
    "$BASE_PATH/alpa_four_prerevamp"
)

for dir in "${CRITICAL_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        chown ing:ing "$dir"
        chmod 755 "$dir"
    fi
done

# 6. Remove setuid/setgid bits in one pass
echo "🧹 Cleaning special permissions..."
find "$BASE_PATH" -type f \( -perm -4000 -o -perm -2000 \) -exec chmod -s {} +

echo "🎉 PERMISSIONS FIXED!"
echo "📊 Summary:"
echo "   • Owner: ing:ing for all files/folders"
echo "   • Directories: 755 (rwxr-xr-x)"
echo "   • Files: 644 (rw-r--r--)"
echo "   • Scripts: 755 (rwxr-xr-x)"

# 7. Test access to key locations
echo ""
echo "🧪 Testing access..."
TEST_DIRS=(
    "$BASE_PATH/RICK"
    "$BASE_PATH/FOUR_horsemen"
    "$BASE_PATH"
)

for test_dir in "${TEST_DIRS[@]}"; do
    if [ -d "$test_dir" ] && [ -r "$test_dir" ] && [ -w "$test_dir" ] && [ -x "$test_dir" ]; then
        echo "✅ Access confirmed: $test_dir"
    elif [ -d "$test_dir" ]; then
        echo "⚠️  Access issue: $test_dir"
    fi
done

echo ""
echo "🚀 Ready for deployment!"
