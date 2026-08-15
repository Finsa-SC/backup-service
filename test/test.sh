#!/usr/bin/env bash

backuper=".venv/bin/backuper"
temporary_dir="/tmp/auto-test"
backup_dir="$temporary_dir/backup"
extract_dir="$temporary_dir/extract"
archive_dir="$temporary_dir/archive"
restore_dir="$temporary_dir/restore"
target_config="$temporary_dir/etc/arg-init-test.toml"
recovery_dir="$temporary_dir/recovery"

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
        success "RESTORE file test export exists"
    else
        failed "RESTORE file test export doesn't exists"
    fi
}

test_encryption() {
    local encryption_path="$temporary_dir/etc/encryption-init-test.toml"
    local master_key="$temporary_dir/etc/master.key"
    local wrong_master_key="$temporary_dir/etc/wrong_master.key"
    echo "hello, world!" > "$master_key"
    echo "halo, dunia!" > "$wrong_master_key"

    "$backuper" init "$temporary_dir/etc/encryption-init-test.toml" \
        --target "$temporary_dir" \
        --destination "$backup_dir" \
        --retention 4 \
        --link-mode "ignore" \
        --compression "gzip" \
        --archive-path "$archive_dir" \
        --key-path "$master_key" \
        1> /dev/null

    if "$backuper" backup --config "$encryption_path" 1> /dev/null; then
        success "ENCRYPTION test make one encrypted file passed"
    else
        failed "ENCRYPTION test make one encrypted file failed"
    fi

    local newest
    newest="$(ls -1t "$backup_dir"/*.enc 2>/dev/null | head -n 1)"
    "$backuper" restore --file "$newest" --archive-path "$backup_dir" --destination "$recovery_dir" --key-path "$wrong_master_key" 1> /dev/null
    if "$backuper" restore \
        --file "$newest" \
        --archive-path "$backup_dir" \
        --destination "$recovery_dir" \
        --key-path "$wrong_master_key" 1>/dev/null; then

        failed "ENCRYPTION invalid key was accepted"
    else
        if [ -e "$newest" ]; then
            success "ENCRYPTION invalid key rejected and backup preserved"
        else
            failed "ENCRYPTION invalid key rejected but backup was removed"
        fi
    fi

    if "$backuper" restore --file "$newest" --archive-path "$backup_dir" --destination "$recovery_dir" --key-path "$master_key" 1> /dev/null; then
        success "ENCRYPTION test passed to restore encrypted data"
    else
        failed "ENCRYPTION test failed to restore encrypted data"
    fi
}

test_encryption_empty_key() {
    local encryption_path="$temporary_dir/etc/encryption-empty-key-test.toml"
    local master_key="$temporary_dir/etc/empty_master.key"
    local empty_key_backup="$temporary_dir/empty-key-backup"

    mkdir -p "$empty_key_backup"
    : > "$master_key"

    "$backuper" init "$encryption_path" \
        --target "$temporary_dir" \
        --destination "$empty_key_backup" \
        --compression "gzip" \
        --key-path "$master_key" \
        1> /dev/null

    if "$backuper" backup --config "$encryption_path" 1> /dev/null; then
        failed "ENCRYPTION empty key was accepted"
        return
    fi

    if compgen -G "$empty_key_backup/*.tar.gz" > /dev/null; then
        failed "ENCRYPTION empty key created backup artifact"
        return
    fi

    if compgen -G "$empty_key_backup/*.sha256" > /dev/null; then
        failed "ENCRYPTION empty key created checksum"
        return
    fi

    success "ENCRYPTION empty key rejected before backup"

    chmod 000 "$master_key"
    "$backuper" backup --config "$encryption_path"
}

main() {
    info "Starting auto test for backuper"
    mkdir -p "$temporary_dir"
    mkdir -p "$backup_dir"
    mkdir -p "$extract_dir"
    mkdir -p "$archive_dir"
    mkdir -p "$restore_dir"
    mkdir -p "$recovery_dir"

    test_init
    test_dry_run
    test_backup
    test_retention
    test_verify
    test_restore
    test_encryption
    test_encryption_empty_key

    info "Cleaning up test directory"
    rm -rf "$temporary_dir"
}

main

