#!/usr/bin/env bash

backuper=".venv/bin/backuper"

temporary_dir="/tmp/auto-test"
backup_dir="$temporary_dir/backup"
extract_dir="$temporary_dir/extract"
archive_dir="$temporary_dir/archive"
restore_dir="$temporary_dir/restore"
recovery_dir="$temporary_dir/recovery"
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
info() {
    echo -e "${BLUE}${BOLD}[*]${RESET} $*"
}

success() {
    echo -e "${GREEN}${BOLD}[✓]${RESET} $*"
}

warn() {
    echo -e "${YELLOW}${BOLD}[!]${RESET} $*"
}

failed() {
    echo -e "${RED}${BOLD}[✗]${RESET} $*"
}

skip() {
    echo -e "${DIM}[~] $*${RESET}"
}

section() {
    echo -e "\n${CYAN}${BOLD}══ $* ══${RESET}"
}

latest_backup() {
    find "$1" \
        -type f \
        ! -name '*.sha256' \
        -printf '%T@ %p\n' 2>/dev/null |
        sort -nr |
        head -n 1 |
        cut -d' ' -f2-
}


test_init() {
    section "INIT"

    mkdir -p "$temporary_dir/etc"

    if "$backuper" init \
        "$temporary_dir/etc/default-init-test.toml" \
        1> /dev/null; then

        success "INIT default test passed"
    else
        failed "INIT default test failed"
    fi

    if "$backuper" init \
        "$temporary_dir/etc/arg-init-test.toml" \
        --target "$temporary_dir" \
        --destination "$backup_dir" \
        --retention 4 \
        --link-mode "ignore" \
        --compression "gzip" \
        --archive-path "$archive_dir" \
        1> /dev/null; then

        success "INIT with argument test passed"
    else
        failed "INIT with argument test failed"
    fi
}


test_dry_run() {
    section "DRY RUN"

    if "$backuper" backup \
        --dry-run \
        --config "$target_config" \
        1> /dev/null; then

        success "DRY-RUN execution passed"
    else
        failed "DRY-RUN execution failed"
        return
    fi

    if compgen -G "$backup_dir/*" > /dev/null; then
        failed "DRY-RUN created backup artifacts"
    else
        success "DRY-RUN created no backup artifacts"
    fi
}


test_backup() {
    section "BACKUP"

    if "$backuper" backup \
        --config "$target_config" \
        1> /dev/null; then

        success "BACKUP test passed"
    else
        failed "BACKUP test failed"
    fi
}


test_retention() {
    section "RETENTION"

    "$backuper" backup --config "$target_config" 1> /dev/null
    "$backuper" backup --config "$target_config" 1> /dev/null

    if ! compgen -G "$archive_dir/*" > /dev/null; then
        success "RETENTION initial archive state passed"
    else
        failed "RETENTION initial archive state failed"
    fi

    "$backuper" backup --config "$target_config" 1> /dev/null
    "$backuper" backup --config "$target_config" 1> /dev/null

    if compgen -G "$archive_dir/*" > /dev/null; then
        success "RETENTION archive creation passed"
    else
        failed "RETENTION archive creation failed"
    fi
}


test_verify() {
    section "VERIFY"

    if ! "$backuper" backup \
        --config "$target_config" \
        1> /dev/null; then

        failed "VERIFY setup backup failed"
        return
    fi

    local backup_file
    backup_file="$(latest_backup "$backup_dir")"

    if [ -z "$backup_file" ]; then
        failed "VERIFY could not find backup file"
        return
    fi

    if "$backuper" verify \
        --file "$backup_file" \
        1> /dev/null; then

        success "VERIFY with file path passed"
    else
        failed "VERIFY with file path failed"
    fi
}


test_restore() {
    section "RESTORE"

    if ! "$backuper" backup \
        --config "$target_config" \
        1> /dev/null; then

        failed "RESTORE setup backup failed"
        return
    fi

    local backup_file
    backup_file="$(latest_backup "$backup_dir")"

    if [ -z "$backup_file" ]; then
        failed "RESTORE could not find backup file"
        return
    fi

    if "$backuper" restore \
        --file "$backup_file" \
        --destination "$restore_dir" \
        1> /dev/null; then

        success "RESTORE with file path passed"
    else
        failed "RESTORE with file path failed"
    fi

    if compgen -G "$restore_dir/*" > /dev/null; then
        success "RESTORE extracted data exists"
    else
        failed "RESTORE extracted data does not exist"
    fi
}


test_encryption() {
    section "ENCRYPTION"

    local encryption_path="$temporary_dir/etc/encryption-init-test.toml"
    local master_key="$temporary_dir/etc/master.key"
    local wrong_master_key="$temporary_dir/etc/wrong_master.key"

    echo "hello, world!" > "$master_key"
    echo "halo, dunia!" > "$wrong_master_key"

    if ! "$backuper" init \
        "$encryption_path" \
        --target "$temporary_dir" \
        --destination "$backup_dir" \
        --retention 4 \
        --link-mode "ignore" \
        --compression "gzip" \
        --archive-path "$archive_dir" \
        --key-path "$master_key" \
        1> /dev/null; then

        failed "ENCRYPTION init failed"
        return
    fi

    if "$backuper" backup \
        --config "$encryption_path" \
        1> /dev/null; then

        success "ENCRYPTION backup creation passed"
    else
        failed "ENCRYPTION backup creation failed"
        return
    fi

    local newest
    newest="$(latest_backup "$backup_dir")"

    if [ -z "$newest" ]; then
        failed "ENCRYPTION encrypted backup not found"
        return
    fi

    if [[ "$newest" != *.enc ]]; then
        failed "ENCRYPTION backup does not have .enc extension"
        return
    fi

    success "ENCRYPTION produced encrypted backup"

    # ── Wrong key must be rejected
    if "$backuper" restore \
        --file "$newest" \
        --destination "$recovery_dir" \
        --key-path "$wrong_master_key" \
        1> /dev/null; then

        failed "ENCRYPTION invalid key was accepted"
    else
        if [ -e "$newest" ]; then
            success "ENCRYPTION invalid key rejected and backup preserved"
        else
            failed "ENCRYPTION invalid key rejected but backup was removed"
        fi
    fi

    # ── Correct key must restore successfully
    if "$backuper" restore \
        --file "$newest" \
        --destination "$recovery_dir" \
        --key-path "$master_key" \
        1> /dev/null; then

        success "ENCRYPTION restore with valid key passed"
    else
        failed "ENCRYPTION restore with valid key failed"
    fi
}


test_encryption_empty_key() {
    section "ENCRYPTION EMPTY KEY"

    local encryption_path="$temporary_dir/etc/encryption-empty-key-test.toml"
    local master_key="$temporary_dir/etc/empty_master.key"
    local empty_key_backup="$temporary_dir/empty-key-backup"

    mkdir -p "$empty_key_backup"

    : > "$master_key"

    "$backuper" init \
        "$encryption_path" \
        --target "$temporary_dir" \
        --destination "$empty_key_backup" \
        --compression "gzip" \
        --key-path "$master_key" \
        1> /dev/null

    if "$backuper" backup \
        --config "$encryption_path" \
        1> /dev/null; then

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