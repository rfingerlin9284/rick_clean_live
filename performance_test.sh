#!/bin/bash
# Performance comparison test for permission fixing scripts
# Creates a test directory structure and times both original and optimized approaches

set -e

TEST_BASE="/tmp/perf_test_$$"
FILE_COUNT=1000
DIR_DEPTH=3

echo "🧪 Performance Comparison Test"
echo "================================"
echo ""

# Create test directory structure
echo "📁 Creating test directory with $FILE_COUNT files..."
mkdir -p "$TEST_BASE"
cd "$TEST_BASE"

# Create directory structure
for i in $(seq 1 10); do
    mkdir -p "dir$i/subdir1/subdir2"
    mkdir -p "dir$i/.venv/bin"
    mkdir -p "dir$i/venv/bin"
done

# Create various file types
for i in $(seq 1 $FILE_COUNT); do
    dir=$((i % 10 + 1))
    case $((i % 10)) in
        0|1) touch "dir$dir/file$i.sh" ;;
        2|3) touch "dir$dir/file$i.py" ;;
        4) touch "dir$dir/autonomous_startup$i.sh" ;;
        5) mkdir -p "dir$dir/subdir1" && touch "dir$dir/subdir1/file$i.rb" ;;
        6) mkdir -p "dir$dir/.venv/bin" && touch "dir$dir/.venv/bin/python$i" ;;
        7) mkdir -p "dir$dir/venv/bin" && touch "dir$dir/venv/bin/activate$i" ;;
        *) mkdir -p "dir$dir/subdir2" && touch "dir$dir/subdir2/data$i.txt" ;;
    esac
done

echo "✅ Created test structure: $(find "$TEST_BASE" -type f | wc -l) files, $(find "$TEST_BASE" -type d | wc -l) directories"
echo ""

# Test original approach (multiple separate find commands)
echo "⏱️  Testing ORIGINAL approach (multiple find commands)..."
start_time=$(date +%s.%N)

find "$TEST_BASE" -type d -exec chmod 755 {} \;
find "$TEST_BASE" -type f -exec chmod 644 {} \;
find "$TEST_BASE" -type f \( -name "*.sh" \) -exec chmod 755 {} \;
find "$TEST_BASE" -type f \( -name "*.py" \) -exec chmod 755 {} \;
find "$TEST_BASE" -type f \( -name "*.pl" \) -exec chmod 755 {} \;
find "$TEST_BASE" -type f \( -name "*.rb" \) -exec chmod 755 {} \;
find "$TEST_BASE" -type f -name "autonomous_startup*" -exec chmod 755 {} \;
find "$TEST_BASE" -type f -name "live_predict*" -exec chmod 755 {} \;
find "$TEST_BASE" -path "*/.venv/bin/*" -exec chmod 755 {} \;
find "$TEST_BASE" -path "*/venv/bin/*" -exec chmod 755 {} \;

end_time=$(date +%s.%N)
original_time=$(echo "$end_time - $start_time" | bc)

echo "✅ Original approach completed in: ${original_time}s"
echo ""

# Reset permissions for fair comparison
find "$TEST_BASE" -type f -exec chmod 600 {} + 2>/dev/null
find "$TEST_BASE" -type d -exec chmod 700 {} + 2>/dev/null

# Test optimized approach (consolidated find commands with batching)
echo "⏱️  Testing OPTIMIZED approach (consolidated + batched)..."
start_time=$(date +%s.%N)

find "$TEST_BASE" -type d -exec chmod 755 {} +
find "$TEST_BASE" -type f -exec chmod 644 {} +

find "$TEST_BASE" -type f \( \
    -name "*.sh" \
    -o -name "*.py" \
    -o -name "*.pl" \
    -o -name "*.rb" \
    -o -name "autonomous_startup*" \
    -o -name "live_predict*" \
\) -exec chmod 755 {} +

find "$TEST_BASE" -type f \( \
    -path "*/.venv/bin/*" \
    -o -path "*/venv/bin/*" \
\) -exec chmod 755 {} +

end_time=$(date +%s.%N)
optimized_time=$(echo "$end_time - $start_time" | bc)

echo "✅ Optimized approach completed in: ${optimized_time}s"
echo ""

# Calculate improvement
if command -v bc >/dev/null 2>&1 && (( $(echo "$optimized_time > 0" | bc -l) )); then
    speedup=$(echo "scale=2; $original_time / $optimized_time" | bc)
    improvement=$(echo "scale=1; ($original_time - $optimized_time) / $original_time * 100" | bc)
    
    echo "📊 Performance Comparison:"
    echo "   Original time:  ${original_time}s"
    echo "   Optimized time: ${optimized_time}s"
    echo "   Speedup:        ${speedup}x faster"
    echo "   Improvement:    ${improvement}% faster"
else
    echo "📊 Performance Comparison:"
    echo "   Original time:  ${original_time}s"
    echo "   Optimized time: ${optimized_time}s"
fi

echo ""
echo "🧹 Cleaning up test directory..."
rm -rf "$TEST_BASE"
echo "✅ Done!"
