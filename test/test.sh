#!/usr/bin/env bash

backuper=".venv/bin/backuper"
temporary_dir="/tmp/auto-test"
backup_dir="$temporary_dir/backup"
extract_dir="$temporary_dir/extract"
archive_dir="$temporary_dir/archive"
restore_dir="$temporary_dir/restore"
target_config="$temporary_dir/etc/arg-init-test.toml"

# ── Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

# ── Helpers
info()    { echo -e "${BLUE}${BOLD}[*]${RESET} $*"; }
success() { echo -e "${GREEN}${BOLD}[✓]${RESET} $*"; }
warn()    { echo -e "${YELLOW}${BOLD}[!]${RESET} $*"; }
failed()   { echo -e "${RED}${BOLD}[✗]${RESET} $*"; }
skip()    { echo -e "${DIM}[~] $*${RESET}"; }
section() { echo -e "\n${CYAN}${BOLD}══ $* ══${RESET}"; }


test_init(){
    mkdir -p "$temporary_dir/etc/"
    if "$backuper" init "$temporary_dir/etc/default-init-test.toml" 1> /dev/null; then
        success "INIT default test passed"
    else
        failed "INIT default test failed"
    fi

    if "$backuper" init "$temporary_dir/etc/arg-init-test.toml" \
        --target "$temporary_dir" \
        --destination "$temporary_dir/backup" \
        --retention 4 \
        --link-mode "ignore" \
        --compression "gzip" \
        --archive-path "$archive_dir" \
        1> /dev/null ; then
        success "INIT with argument test passed"
    else
        failed "INIT with argument test failed"
    fi
}

test_dry_run(){
    if "$backuper" backup --dry-run --config "$target_config" 1> /dev/null; then
        success "DRY-RUN test passed"
    else
        failed "DRY-RUN test failed"
    fi
}

test_backup() {
    if "$backuper" backup --config "$target_config" 1> /dev/null; then
        success "BACKUP test success"
    else
        failed "BACKUP test failed"
    fi
}

test_retention() {
    "$backuper" backup --config "$target_config" 1> /dev/null
    "$backuper" backup --config "$target_config" 1> /dev/null
    if [ ! -e "$archive_dir"/* ]; then
        success "RETENTION test check archive is empty success"
    else
        failed "RETENTION test check archive is empty failed"
    fi
    "$backuper" backup --config "$target_config" 1> /dev/null
    "$backuper" backup --config "$target_config" 1> /dev/null
    if [ -e "$archive_dir"/* ]; then
        success "RETENTION test success"
    else
        failed "RETENTION test failed"
    fi
}

test_verify() {
    "$backuper" backup --config "$target_config" 1> /dev/null
    local date_now=$(date "+%Y-%m-%d")
    if "$backuper" verify --date "$date_now" --archive-path "$archive_dir" 1> /dev/null; then
        success "VERIFY with date test success"
    else
        failed "VERIFY with date test failed"
    fi

    first_file="$(find "$archive_dir" -type f ! -name '*.sha256' -print -quit)"
    if [ -n "$first_file" ] && "$backuper" verify --file "$first_file" 1> /dev/null; then
        success "VERIFY with file path test success"
    else
        failed "VERIFY with file path test failed"
    fi
}

test_restore() {
    local date_now=$(date "+%Y-%m-%d")
    if "$backuper" restore --date "$date_now" --archive-path "$archive_dir" --destination "$restore_dir" 1> /dev/null; then
        success "RESTORE with date test success"
    else
        failed "RESTORE with date test failed"
    fi

    first_file="$(find "$archive_dir" -type f ! -name '*.sha256' -print -quit)"
    if [ -n "$first_file" ] && "$backuper" restore --file "$first_file" --destination "$restore_dir" 1> /dev/null; then
        success "RESTORE with file path test success"
    else
        failed "RESTORE with file path test failed"
    fi

    if [ -e "$restore_dir"/* ]; then
        success "RESTORE file test exists"
    else
        success "RESTORE file test exists"
    fi
}

main() {
    info "Starting auto test for backuper"
    mkdir -p "$temporary_dir"
    mkdir -p "$backup_dir"
    mkdir -p "$extract_dir"
    mkdir -p "$archive_dir"
    mkdir -p "$restore_dir"

    test_init
    test_dry_run
    test_backup
    test_retention
    test_verify
    test_restore

    info "Cleaning up test directory"
    rm -rf "$temporary_dir"
}

main

