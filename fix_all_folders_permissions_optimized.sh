#!/bin/bash
# === OPTIMIZED COMPREHENSIVE PERMISSIONS FIXER FOR ALL ING FOLDERS ===
# Performance improvements: consolidated find operations, batched exec, reduced redundancy

set -e

BASE_PATH="${1:-/home/ing}"

echo "🔓 FIXING PERMISSIONS FOR ALL FOLDERS UNDER $BASE_PATH ..."

# 1. Take ownership once for all files/directories
echo "📋 Taking ownership of ALL folders and files..."
sudo chown -R ing:ing "$BASE_PATH"

# 2. Set all permissions in a single find traversal (much faster)
echo "🛠️ Setting permissions in optimized single pass..."
find "$BASE_PATH" \( \
    -type d -exec chmod 755 {} + \
    -o -type f -exec chmod 644 {} + \
\)

# 3. Make scripts and executables executable in one pass
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
    -o -name "start*" \
    -o -name "launch*" \
\) -exec chmod 755 {} +

# 4. Fix Python virtual environment binaries in one pass
echo "🐍 Fixing Python virtual environments..."
find "$BASE_PATH" -type f \( \
    -path "*/.venv/bin/*" \
    -o -path "*/venv/bin/*" \
    -o -path "*/venv_*/bin/*" \
\) -exec chmod 755 {} +

# 5. Remove setuid/setgid bits in one pass
echo "🧹 Cleaning special permissions..."
find "$BASE_PATH" -type f \( -perm -4000 -o -perm -2000 \) -exec chmod -s {} +

echo "🎉 PERMISSIONS FIXED FOR ALL FOLDERS!"
echo ""
echo "📊 Summary:"
echo "   • Owner: ing:ing for all files/folders"
echo "   • Directories: 755 (rwxr-xr-x)"
echo "   • Files: 644 (rw-r--r--)"
echo "   • Scripts: 755 (rwxr-xr-x)"

# 6. Test access to critical folders
echo ""
echo "🧪 Testing access to critical folders..."
TEST_FOLDERS=(
    "$BASE_PATH/RICK"
    "$BASE_PATH/LIVE_UNIBOT_RECON"
    "$BASE_PATH/Live_unibot_v001"
    "$BASE_PATH/.ssh"
    "$BASE_PATH/bin"
)

for test_folder in "${TEST_FOLDERS[@]}"; do
    if [ -d "$test_folder" ] && [ -r "$test_folder" ] && [ -w "$test_folder" ] && [ -x "$test_folder" ]; then
        echo "✅ Access confirmed: $test_folder"
    elif [ -d "$test_folder" ]; then
        echo "⚠️  Access issue: $test_folder"
    fi
done

echo ""
echo "🚀 ALL PERMISSIONS SET! Ready for full deployment!"
