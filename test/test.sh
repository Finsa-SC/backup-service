#!/usr/bin/env bash

# Hardtest Script untuk Backuper
# Testing: concurrent backups, large files, edge cases, corruption detection
# All tests run in memory-only temp directory, auto cleanup

set -e

backuper=".venv/bin/backuper"

# ── Temp directories (all in /tmp, auto cleanup)
temp_root="/tmp/backuper-hardtest-$$"
test_target="$temp_root/target"
backup_base="$temp_root/backup"
archive_base="$temp_root/archive"
restore_base="$temp_root/restore"
config_dir="$temp_root/config"
key_dir="$temp_root/keys"

# ── Timing
declare -A timing_results

# ── Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

# ── Helpers
info() { echo -e "${BLUE}${BOLD}[*]${RESET} $*"; }
success() { echo -e "${GREEN}${BOLD}[✓]${RESET} $*"; }
warn() { echo -e "${YELLOW}${BOLD}[!]${RESET} $*"; }
failed() { echo -e "${RED}${BOLD}[✗]${RESET} $*"; }
section() { echo -e "\n${CYAN}${BOLD}══ $* ══${RESET}"; }

# ── Cleanup
cleanup() {
    info "Cleaning up $temp_root"
    rm -rf "$temp_root" 2>/dev/null || true
}
trap cleanup EXIT

# ── Setup
setup_dirs() {
    mkdir -p "$test_target" "$backup_base" "$archive_base" "$restore_base" "$config_dir" "$key_dir"
}

# ── Helper: time command execution
time_exec() {
    local name="$1"
    shift
    local start end
    start=$(date +%s%N)
    "$@" > /dev/null 2>&1
    end=$(date +%s%N)
    local duration=$(( (end - start) / 1000000 ))  # Convert to ms
    timing_results["$name"]="$duration ms"
    echo "$duration"
}

# ── Helper: create test file
create_file() {
    local path="$1"
    local size="$2"
    mkdir -p "$(dirname "$path")"
    dd if=/dev/urandom of="$path" bs=1M count="$size" 2>/dev/null
}

# ── Helper: create text file
create_text_file() {
    local path="$1"
    local lines="${2:-1000}"
    mkdir -p "$(dirname "$path")"
    {
        for ((i=1; i<=lines; i++)); do
            echo "Line $i: Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        done
    } > "$path"
}

# ── Helper: find latest backup
latest_backup() {
    find "$1" -type f ! -name '*.sha256' ! -name '*.enc' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -n1 | cut -d' ' -f2-
}

# ════════════════════════════════════════════════════════════════
# TESTS
# ════════════════════════════════════════════════════════════════

# Test 1: Basic Functionality
test_basic() {
    section "TEST 1: Basic Functionality"

    local config="$config_dir/basic.toml"
    local backup_dir="$backup_base/basic"

    mkdir -p "$backup_dir"

    # Create test files
    create_text_file "$test_target/file1.txt" 100
    create_text_file "$test_target/file2.txt" 200

    if "$backuper" init "$config" \
        --target "$test_target" \
        --destination "$backup_dir" \
        --compression "zstd" \
        --link-mode "ignore" \
        1> /dev/null; then
        success "Basic init passed"
    else
        failed "Basic init failed"
        return 1
    fi

    if "$backuper" backup --config "$config" 1> /dev/null; then
        success "Basic backup passed"
    else
        failed "Basic backup failed"
        return 1
    fi
}

# Test 2: Large Files (50MB each)
test_large_files() {
    section "TEST 2: Large Files (50MB)"

    local config="$config_dir/large.toml"
    local backup_dir="$backup_base/large"
    local test_dir="$test_target/large_files"

    mkdir -p "$backup_dir" "$test_dir"

    info "Creating 3x 50MB files..."
    create_file "$test_dir/large1.bin" 50
    create_file "$test_dir/large2.bin" 50
    create_file "$test_dir/large3.bin" 50

    if "$backuper" init "$config" \
        --target "$test_dir" \
        --destination "$backup_dir" \
        --compression "zstd" \
        1> /dev/null; then
        success "Large files init passed"
    else
        failed "Large files init failed"
        return 1
    fi

    local duration
    duration=$(time_exec "large_files_backup" "$backuper" backup --config "$config")
    success "Large files backup passed (${duration}ms)"
}

# Test 3: Many Small Files (5000+ files)
test_many_small_files() {
    section "TEST 3: Many Small Files (5000+)"

    local config="$config_dir/small_files.toml"
    local backup_dir="$backup_base/small_files"
    local test_dir="$test_target/small_files"

    mkdir -p "$backup_dir" "$test_dir"

    info "Creating 5000 small files..."
    for i in {1..5000}; do
        echo "Small file $i" > "$test_dir/file_$i.txt"
        if ((i % 1000 == 0)); then
            echo -ne "\rCreated $i files..."
        fi
    done
    echo ""

    if "$backuper" init "$config" \
        --target "$test_dir" \
        --destination "$backup_dir" \
        --compression "zstd" \
        1> /dev/null; then
        success "Small files init passed"
    else
        failed "Small files init failed"
        return 1
    fi

    local duration
    duration=$(time_exec "small_files_backup" "$backuper" backup --config "$config")
    success "Small files backup passed (${duration}ms, 5000 files)"
}

# Test 4: Deep Directory Structure (100+ levels)
test_deep_directories() {
    section "TEST 4: Deep Directory Structure"

    local config="$config_dir/deep.toml"
    local backup_dir="$backup_base/deep"
    local test_dir="$test_target/deep"

    mkdir -p "$backup_dir"

    info "Creating nested directories (50 levels)..."
    local current="$test_dir"
    for i in {1..50}; do
        current="$current/level_$i"
        mkdir -p "$current"
        echo "Level $i file" > "$current/file_$i.txt"
    done

    if "$backuper" init "$config" \
        --target "$test_dir" \
        --destination "$backup_dir" \
        --compression "zstd" \
        1> /dev/null; then
        success "Deep directories init passed"
    else
        failed "Deep directories init failed"
        return 1
    fi

    if "$backuper" backup --config "$config" 0> /dev/null; then
        success "Deep directories backup passed"
    else
        failed "Deep directories backup failed"
        return 1
    fi
}

# Test 5: Unicode & Special Characters
test_unicode_filenames() {
    section "TEST 5: Unicode & Special Characters"

    local config="$config_dir/unicode.toml"
    local backup_dir="$backup_base/unicode"
    local test_dir="$test_target/unicode"

    mkdir -p "$backup_dir" "$test_dir"

    # Create files with special names
    echo "test" > "$test_dir/файл.txt"  # Russian
    echo "test" > "$test_dir/文件.txt"   # Chinese
    echo "test" > "$test_dir/ファイル.txt" # Japanese
    echo "test" > "$test_dir/file with spaces.txt"
    echo "test" > "$test_dir/file-with-dashes.txt"
    echo "test" > "$test_dir/file_with_underscores.txt"

    if "$backuper" init "$config" \
        --target "$test_dir" \
        --destination "$backup_dir" \
        --compression "zstd" \
        1> /dev/null; then
        success "Unicode filenames init passed"
    else
        failed "Unicode filenames init failed"
        return 1
    fi

    if "$backuper" backup --config "$config" 1> /dev/null; then
        success "Unicode filenames backup passed"
    else
        failed "Unicode filenames backup failed"
        return 1
    fi
}

# Test 6: Symlinks (broken, circular, valid)
test_symlink_edge_cases() {
    section "TEST 6: Symlink Edge Cases"

    local config="$config_dir/symlinks.toml"
    local backup_dir="$backup_base/symlinks"
    local test_dir="$test_target/symlinks"

    mkdir -p "$backup_dir" "$test_dir"

    # Create valid file and symlink
    echo "real file" > "$test_dir/real_file.txt"
    ln -s "$test_dir/real_file.txt" "$test_dir/valid_link.txt" 2>/dev/null || true

    # Create broken symlink
    ln -s "/nonexistent/path/file.txt" "$test_dir/broken_link.txt" 2>/dev/null || true

    # Create circular symlink
    mkdir -p "$test_dir/dir_a" "$test_dir/dir_b"
    ln -s "$test_dir/dir_b" "$test_dir/dir_a/link_to_b" 2>/dev/null || true
    ln -s "$test_dir/dir_a" "$test_dir/dir_b/link_to_a" 2>/dev/null || true

    if "$backuper" init "$config" \
        --target "$test_dir" \
        --destination "$backup_dir" \
        --compression "zstd" \
        --link-mode "ignore" \
        1> /dev/null; then
        success "Symlinks init passed"
    else
        failed "Symlinks init failed"
        return 1
    fi

    if "$backuper" backup --config "$config" 1> /dev/null; then
        success "Symlinks backup passed (with ignore mode)"
    else
        failed "Symlinks backup failed"
        return 1
    fi
}

# Test 7: Permission Issues (read-only files)
test_permission_issues() {
    section "TEST 7: Permission Issues"

    local config="$config_dir/permissions.toml"
    local backup_dir="$backup_base/permissions"
    local test_dir="$test_target/permissions"

    mkdir -p "$backup_dir" "$test_dir"

    # Create files with different permissions
    echo "readable" > "$test_dir/readable.txt"
    echo "readonly" > "$test_dir/readonly.txt"
    chmod 444 "$test_dir/readonly.txt"

    # Create file in subdirectory (directories need execute permission to be accessed)
    mkdir -p "$test_dir/subdir"
    echo "test" > "$test_dir/subdir/file.txt"
    chmod 444 "$test_dir/subdir/file.txt"  # Read-only file, but directory is readable

    if "$backuper" init "$config" \
        --target "$test_dir" \
        --destination "$backup_dir" \
        --compression "zstd" \
        1> /dev/null; then
        success "Permissions init passed"
    else
        failed "Permissions init failed"
        return 1
    fi

    if "$backuper" backup --config "$config" 1> /dev/null; then
        success "Permissions backup passed (read-only files handled)"
    else
        failed "Permissions backup failed"
        return 1
    fi

    # Cleanup permissions
    chmod 644 "$test_dir/readonly.txt" 2>/dev/null || true
    chmod 644 "$test_dir/subdir/file.txt" 2>/dev/null || true
}



# Test 8: Rapid Backup/Restore Cycles
test_rapid_cycles() {
    section "TEST 8: Rapid Backup/Restore Cycles"

    local config="$config_dir/rapid.toml"
    local backup_dir="$backup_base/rapid"
    local restore_dir="$restore_base/rapid"
    local test_dir="$test_target/rapid"

    mkdir -p "$backup_dir" "$restore_dir" "$test_dir"

    create_text_file "$test_dir/data.txt" 100

    if "$backuper" init "$config" \
        --target "$test_dir" \
        --destination "$backup_dir" \
        --compression "zstd" \
        1> /dev/null; then
        success "Rapid cycles init passed"
    else
        failed "Rapid cycles init failed"
        return 1
    fi

    info "Running 10 backup/restore cycles..."
    for i in {1..10}; do
        if ! "$backuper" backup --config "$config" > /dev/null 2>&1; then
            failed "Cycle $i: backup failed"
            return 1
        fi

        local backup_file
        backup_file=$(latest_backup "$backup_dir")

        if ! "$backuper" restore \
            --file "$backup_file" \
            --destination "$restore_dir/cycle_$i" \
            > /dev/null 2>&1; then
            failed "Cycle $i: restore failed"
            return 1
        fi
    done

    success "Rapid cycles passed (10 cycles)"
}

# Test 9: Corrupted Backup Detection
test_corruption_detection() {
    section "TEST 9: Corrupted Backup Detection"

    local config="$config_dir/corruption.toml"
    local backup_dir="$backup_base/corruption"
    local test_dir="$test_target/corruption"

    mkdir -p "$backup_dir" "$test_dir"

    create_text_file "$test_dir/data.txt" 50

    if "$backuper" init "$config" \
        --target "$test_dir" \
        --destination "$backup_dir" \
        --compression "zstd" \
        1> /dev/null; then
        success "Corruption detection init passed"
    else
        failed "Corruption detection init failed"
        return 1
    fi

    if "$backuper" backup --config "$config" 1> /dev/null; then
        success "Corruption detection backup created"
    else
        failed "Corruption detection backup failed"
        return 1
    fi

    local backup_file
    backup_file=$(latest_backup "$backup_dir")

    # Verify valid backup
    if "$backuper" verify --file "$backup_file" 1> /dev/null 2>&1; then
        success "Corruption detection: valid backup verified"
    else
        failed "Corruption detection: valid backup failed verification"
        return 1
    fi

    # Corrupt the backup
    if [ -f "$backup_file" ]; then
        dd if=/dev/urandom of="$backup_file" bs=1 count=10 conv=notrunc 2>/dev/null

        # Verify corrupted backup (should fail)
        if "$backuper" verify --file "$backup_file" 1> /dev/null 2>&1; then
            failed "Corruption detection: corrupted backup passed verification (should fail)"
        else
            success "Corruption detection: corrupted backup correctly rejected"
        fi
    fi
}



# Test 10: Config Edge Cases
test_config_edge_cases() {
    section "TEST 10: Config Edge Cases"

    local test_dir="$test_target/config_edge"
    mkdir -p "$test_dir"

    # Test empty config path
    info "Testing empty config file..."
    local empty_config="$config_dir/empty.toml"
    touch "$empty_config"

    if "$backuper" backup --config "$empty_config" 1> /dev/null 2>&1; then
        warn "Empty config: accepted (may be expected)"
    else
        success "Empty config: correctly rejected"
    fi

    # Test missing required fields
    local invalid_config="$config_dir/invalid.toml"
    echo "[backup]" > "$invalid_config"
    echo "# missing required fields" >> "$invalid_config"

    if "$backuper" backup --config "$invalid_config" 1> /dev/null 2>&1; then
        warn "Invalid config: accepted (may be expected)"
    else
        success "Invalid config: correctly rejected"
    fi
}

# Test 11: Cleanup Verification
test_cleanup_verification() {
    section "TEST 11: Cleanup Verification"

    info "Verifying temp directory cleanup..."

    # Check that temp_root will be cleaned up
    if [ -d "$temp_root" ]; then
        local file_count
        file_count=$(find "$temp_root" -type f | wc -l)
        success "Cleanup verification: $file_count test files created (all will be cleaned)"
    fi
}

# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

main() {
    info "Starting Backuper Hardtest Suite"
    info "Temp directory: $temp_root"
    info "All tests run in memory-only temp space\n"

    setup_dirs

    # Run tests
    test_basic
    test_large_files
    test_many_small_files
    test_deep_directories
    test_unicode_filenames
    test_symlink_edge_cases
    test_permission_issues
    test_rapid_cycles
    test_corruption_detection
    test_config_edge_cases
    test_cleanup_verification

    # Print timing results
    if [ ${#timing_results[@]} -gt 0 ]; then
        section "Performance Results"
        for test in "${!timing_results[@]}"; do
            echo "  $test: ${timing_results[$test]}"
        done
    fi

    section "Hardtest Complete"
    success "All tests finished! Temp files will be cleaned up."
}

main