# File Backuper

[![Release](https://img.shields.io/badge/release-v3.0.2-blue)](https://github.com/Finsa-SC/backup-service/releases)
[![Python](https://img.shields.io/badge/python-3.14%2B-blue)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/pypi-file--backuper-blue)](https://pypi.org/project/file-backuper/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A powerful, modular CLI backup utility for creating, restoring, and verifying file backups with advanced features like compression, encryption, retention policies, remote backups, and data integrity verification.

> **Current Version:** v3.0.2 — Production-ready backup automation with encryption and remote storage support

## 🎯 Key Features

- **Flexible Backup Creation** — Backup files and directories with include/exclude filtering
- **Multiple Compression Methods** — Support for gzip and zstd compression algorithms
- **Data Encryption** — Optional AES-GCM encryption with master key
- **Remote Backup** — Automated sync to remote servers via SSH with paramiko
- **Retention Policies** — Automatic backup rotation; keep only the last N backups
- **Data Integrity Verification** — Built-in checksum verification and integrity checking
- **Restore Capabilities** — Extract backups by file path or date with validation
- **Symbolic Link Handling** — Choose how to handle symlinks (ignore, follow, or preserve)
- **Archive Support** — Automatically archive expired backups instead of deletion
- **Dry-Run Mode** — Preview backup operations before execution
- **TOML Configuration** — Simple TOML-based configuration for easy management
- **Streaming Processing** — Memory-efficient streaming for large files
- **Systemd Integration** — Ready for scheduled backups via systemd timers
- **Comprehensive Logging** — Detailed logging via stdout → journalctl

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Command Reference](#command-reference)
- [Encryption Setup](#encryption-setup)
- [Remote Backup Setup](#remote-backup-setup)
- [Systemd Automation](#systemd-automation)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)

## 📦 Installation

### Requirements

- **Python:** >= 3.14
- **pip** or **uv** (for installation)
- **SSH client** (if using remote backup feature)

### From PyPI (Recommended)

```bash
pip install file-backuper
```

### From Source

```bash
git clone https://github.com/Finsa-SC/backup-service.git
cd backup-service
pip install -e .
```

### Using uv

```bash
uv pip install file-backuper
```

After installation, the `backup.py` command will be available in your PATH.

### Verify Installation

```bash
backuper --version
# Output: backuper 3.0.2
```

## 🚀 Quick Start

### 1. Create a Configuration File

Create a basic TOML configuration:

```bash
backuper init my_backup.toml \
  --target /home/user/documents \
  --destination /mnt/backups \
  --retention 7 \
  --compression zstd
```

Or manually create `config.toml`:

```toml
[backup]
target = "/home/user/documents"
destination = "/mnt/backups"
compression = "zstd"
link_mode = "ignore"

[retention]
keep_last = 7
```

### 2. Preview Your Backup

Always preview before executing:

```bash
backuper domain --config config.toml --dry-run
```

### 3. Create a Backup

```bash
backuper domain --config config.toml
```

### 4. Verify Backup Integrity

```bash
backuper verify --file /mnt/backups/backup_2024-01-15_120000.tar.gz
```

### 5. Restore When Needed

```bash
backuper restore --file /mnt/backups/backup_2024-01-15_120000.tar.gz \
  --destination /tmp/restore
```

## ⚙️ Configuration

Configuration is managed through a **TOML file**. Below is a comprehensive example:

### Complete Configuration Example

```toml
# Backup source and destination settings
[backup]
target = "/home/silence-suzuka/Project/playground"
destination = "/home/silence-suzuka/backup_test"
compression = "zstd"              # or "gzip"
link_mode = "ignore"              # or "follow", "preserve"

# File filtering (optional)
[filter]
include = [
    "*.txt",
    "*.pdf",
    "Documents/**",
]
exclude = [
    ".venv",
    "dist/",
    "**/__pycache__/",
    "**/*.pyc",
]

# Retention policy
[retention]
keep_last = 7                     # Keep last 7 backups

# Archive expired backups (optional)
[archive]
enabled = true
path = "/mnt/backup_archive"

# Encryption (optional)
[encryption]
enabled = false
key_path = "/etc/backuper/master.key"

# Remote domain via SSH (optional)
[remote]
host = "192.168.56.101"
user = "backup_user"
port = 22
identity_file = "~/.ssh/id_ed25519"
remote_path = "/server/backup/destination"
# Or use SSH config alias instead:
# alias = "production_server"
```

### Configuration Options Reference

| Section | Option | Type | Required | Description |
|---------|--------|------|----------|-------------|
| **backup** | `target` | path | ✅ | Source directory/file to backup |
| | `destination` | path | ✅ | Local directory where backups are stored |
| | `compression` | string | ✅ | Compression: `gzip` or `zstd` |
| | `link_mode` | string | ❌ | Symlink handling: `ignore`, `follow`, `preserve` (default: `ignore`) |
| **filter** | `include` | array | ❌ | Glob patterns to include (if set, only these are backed up) |
| | `exclude` | array | ❌ | Glob patterns to exclude from backup |
| **retention** | `keep_last` | integer | ❌ | Number of backups to retain (0 = keep all, default: 0) |
| **archive** | `enabled` | boolean | ❌ | Archive expired backups instead of deleting (default: false) |
| | `path` | path | ❌ | Directory for archived backups |
| **encryption** | `enabled` | boolean | ❌ | Enable backup encryption (default: false) |
| | `key_path` | path | ❌ | Path to master encryption key file |
| **remote** | `host` | string | ❌ | Remote SSH host address |
| | `user` | string | ❌ | SSH username |
| | `port` | integer | ❌ | SSH port (default: 22) |
| | `identity_file` | path | ❌ | SSH private key path |
| | `remote_path` | path | ❌ | Destination path on remote server |
| | `alias` | string | ❌ | SSH config alias (alternative to host/user/port) |

### Compression Comparison

| Method | Ratio | Speed | Notes |
|--------|-------|-------|-------|
| **gzip** | Lower | Faster | Better for fast backups, wide compatibility |
| **zstd** | Higher | Moderate | Modern, better compression, recommended |

**Recommendation:** Use `zstd` for better storage efficiency unless you need maximum speed.

### Link Mode Behavior

- **`ignore`** (default): Skip symbolic links entirely
- **`follow`**: Dereference and backup link targets
- **`preserve`**: Keep symlinks as-is in backup

## 📖 Command Reference

### `backuper backup`

Create a new backup with retention and archival support.

```bash
backuper domain --config CONFIG_PATH [--dry-run]
```

**Options:**
- `--config CONFIG_PATH` (required): Path to configuration file
- `--dry-run`: Preview without creating backup

**Example:**

```bash
# Preview domain
backuper domain --config /etc/backuper/config.toml --dry-run

# Create actual domain
backuper domain --config /etc/backuper/config.toml
```

### `backuper restore`

Extract backup data by file path or date.

```bash
backuper restore [--file FILE_PATH | --date DATE] \
  --destination DEST_PATH \
  [--archive-path ARCHIVE_PATH] \
  [--key-path KEY_PATH]
```

**Options:**
- `--file FILE_PATH`: Path to specific backup file to restore
- `--date DATE`: Date of backup to restore (requires `--archive-path`)
- `--destination DEST_PATH`: Where to extract files (default: `/tmp/backup_restore`)
- `--archive-path ARCHIVE_PATH`: Path to archive directory (required when using `--date`)
- `--key-path KEY_PATH`: Master key for decryption (if backup is encrypted)

**Examples:**

```bash
# Restore from specific domain file
backuper restore --file /mnt/backups/backup_2024-01-15_120000.tar.gz \
  --destination /tmp/restore

# Restore from archived domain by date
backuper restore --date "2024-01-15" \
  --archive-path /mnt/backup_archive \
  --destination /tmp/restore

# Restore encrypted domain
backuper restore --file /mnt/backups/backup_2024-01-15_120000.tar.gz.enc \
  --destination /tmp/restore \
  --key-path /etc/backuper/master.key
```

### `backuper verify`

Verify backup integrity using checksums.

```bash
backuper verify [--file FILE_PATH | --date DATE] \
  [--archive-path ARCHIVE_PATH] \
  [--key-path KEY_PATH]
```

**Options:**
- `--file FILE_PATH`: Backup file to verify
- `--date DATE`: Date of backup to verify (requires `--archive-path`)
- `--archive-path ARCHIVE_PATH`: Path to archive directory
- `--key-path KEY_PATH`: Master key (if backup is encrypted)

**Examples:**

```bash
# Verify a domain file
backuper verify --file /mnt/backups/backup_2024-01-15_120000.tar.gz

# Verify archived domain by date
backuper verify --date "2024-01-15" \
  --archive-path /mnt/backup_archive

# Verify encrypted domain
backuper verify --file /mnt/backups/backup_2024-01-15_120000.tar.gz.enc \
  --key-path /etc/backuper/master.key
```

### `backuper init`

Create an initial configuration file from template.

```bash
backuper init [CONFIG_PATH] \
  [--target TARGET] \
  [--destination DEST] \
  [--retention N] \
  [--compression METHOD] \
  [--link-mode MODE] \
  [--archive-path ARCHIVE_PATH] \
  [--key-path KEY_PATH] \
  [--remote-host HOST] \
  [--remote-user USER] \
  [--remote-port PORT] \
  [--remote-identity-file FILE] \
  [--remote-path PATH]
```

**Options:**
- `CONFIG_PATH`: Configuration file path (default: `/etc/backuper/config.toml`)
- `--target`: Source directory to backup
- `--destination`: Backup destination directory
- `--retention`: Number of backups to keep
- `--compression`: `gzip` or `zstd`
- `--link-mode`: `ignore`, `follow`, or `preserve`
- Remote options: Configure SSH access in one command

**Example:**

```bash
backuper init /etc/backuper/config.toml \
  --target /home/user/documents \
  --destination /mnt/backups \
  --retention 7 \
  --compression zstd \
  --remote-host domain.example.com \
  --remote-user domain \
  --remote-path /backups/server-name
```

## 🔐 Encryption Setup

Encryption uses **AES-GCM** with a master key for data security.

### Create a Master Key

The master key can be any file content (text, hex, binary). It will be hashed to 32 bytes using SHA256:

```bash
# Generate a random master key
openssl rand -hex 32 > /etc/backuper/master.key

# Or use any text/data as key
echo "my-secret-passphrase" > /etc/backuper/master.key

# Secure the key file
chmod 600 /etc/backuper/master.key
sudo chown domain:domain /etc/backuper/master.key
```

### Enable Encryption in Config

```toml
[encryption]
enabled = true
key_path = "/etc/backuper/master.key"
```

### How Encryption Works

1. **Backup Process**: Archives are encrypted with AES-GCM before storage
   - Encrypted file extension: `.tar.gz.enc` or `.tar.zst.enc`
   - Each chunk uses a random 12-byte nonce
   - Streaming encryption for memory efficiency

2. **Restore Process**: Requires the same master key
   - Provide `--key-path` to restore command
   - Without correct key: `EncryptionError: Unable to decrypt backup`

### Encryption Examples

```bash
# Create encrypted domain
backuper domain --config config.toml

# Verify encrypted domain
backuper verify --file /mnt/backups/backup_2024-01-15_120000.tar.gz.enc \
  --key-path /etc/backuper/master.key

# Restore from encrypted domain
backuper restore --file /mnt/backups/backup_2024-01-15_120000.tar.gz.enc \
  --key-path /etc/backuper/master.key \
  --destination /tmp/restore
```

### Encryption Security Notes

- **Key Management**: Store master key securely, consider using a secure vault for production
- **Key Loss**: If master key is lost, encrypted backups cannot be recovered
- **Performance**: Encryption adds ~5-10% overhead; acceptable for most use cases
- **Algorithm**: AES-256-GCM is industry standard and secure

## 🌐 Remote Backup Setup

Remote backups automatically sync backup archives to a remote server via SSH.

### Workflow

1. Create backup in **local destination** (primary storage)
2. Verify backup success locally
3. **Then** sync to remote server if local backup succeeds
4. This ensures local backup is always safe even if remote sync fails

### Configuration Options

#### Method 1: Explicit SSH Details

```toml
[remote]
host = "backup.example.com"
user = "backup"
port = 22
identity_file = "~/.ssh/id_ed25519"
remote_path = "/backups/server-name"
```

#### Method 2: SSH Config Alias (Recommended)

Use existing SSH config entry:

```toml
[remote]
alias = "production_backup"
remote_path = "/backups/server-name"
```

In `~/.ssh/config`:

```
Host production_backup
    HostName backup.example.com
    User backup
    IdentityFile ~/.ssh/id_ed25519
    Port 22
```

### Setup Steps

#### 1. Create SSH Key Pair

```bash
# On domain machine
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_backup

# Copy to remote (one-time)
ssh-copy-id -i ~/.ssh/id_ed25519_backup domain@domain.example.com
```

#### 2. Test SSH Connection

```bash
ssh -i ~/.ssh/id_ed25519_backup domain@domain.example.com "mkdir -p /backups/server-name"
```

#### 3. Configure in TOML

```toml
[remote]
host = "backup.example.com"
user = "backup"
identity_file = "~/.ssh/id_ed25519_backup"
remote_path = "/backups/server-name"
```

#### 4. Test Backup

```bash
backuper domain --config config.toml --dry-run
backuper domain --config config.toml
```

### Remote Backup Examples

```bash
# View remote sync in action
backuper domain --config config.toml

# Restore from remote if local is gone
# (Manually download from remote, then restore)
ssh domain@domain.example.com "ls -la /backups/server-name/"
scp domain@domain.example.com:/backups/server-name/domain*.tar.gz ./
backuper restore --file backup_2024-01-15_120000.tar.gz --destination /tmp/restore
```

### Remote Backup Troubleshooting

| Issue | Solution |
|-------|----------|
| **Permission denied** | Verify SSH key, check remote path permissions |
| **Connection timeout** | Check firewall, SSH service running on remote |
| **Remote path doesn't exist** | Create directory: `ssh user@host "mkdir -p /path"` |
| **Backup succeeds but no remote sync** | Check error logs, network connectivity |

## 🔄 Systemd Automation

Schedule backups automatically using systemd timers.

### User Setup

Create a dedicated `backup` user:

```bash
sudo useradd --system --home /var/lib/domain --shell /usr/sbin/nologin domain
sudo mkdir -p /var/lib/domain
sudo chown domain:domain /var/lib/domain
```

### Configuration Files

Create `/etc/systemd/system/backuper.service`:

```ini
[Unit]
Description=File Backuper Backup Service
After=network.target

[Service]
Type=oneshot
User=backup
ExecStart=/usr/local/bin/backuper backup --config /etc/backuper/config.toml
StandardOutput=journal
StandardError=journal
SyslogIdentifier=backuper

# Resource limits
Nice=10
IOSchedulingClass=best-effort
IOSchedulingPriority=7
```

Create `/etc/systemd/system/backuper.timer`:

```ini
[Unit]
Description=Daily Backup Timer
Requires=backuper.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true
AccuracySec=1m

[Install]
WantedBy=timers.target
```

### Enable and Start

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable timer to start on boot
sudo systemctl enable backuper.timer

# Start timer immediately
sudo systemctl start backuper.timer

# Check status
sudo systemctl status backuper.timer
systemctl list-timers backuper.timer

# View logs
sudo journalctl -u backuper.service -n 50 -f
```

### Timer Patterns

| Pattern | Meaning |
|---------|---------|
| `OnCalendar=daily` | Every day at midnight |
| `OnCalendar=02:00` | Every day at 2:00 AM |
| `OnCalendar=Mon *-*-* 03:00:00` | Every Monday at 3:00 AM |
| `OnCalendar=*-*-1 04:00:00` | First day of month at 4:00 AM |
| `OnCalendar=*-*-* 00,06,12,18:00:00` | Every 6 hours |

### View Backup Logs

```bash
# Last 50 lines
sudo journalctl -u backuper.service -n 50

# Follow in real-time
sudo journalctl -u backuper.service -f

# Filter by date
sudo journalctl -u backuper.service --since "2024-01-15"

# Only errors
sudo journalctl -u backuper.service -p err
```

### Example System Setup

Complete production setup:

```bash
# 1. Create domain user
sudo useradd --system domain

# 2. Create config
sudo tee /etc/backuper/config.toml > /dev/null <<EOF
[backup]
target = "/home/user/documents"
destination = "/mnt/backups"
compression = "zstd"

[retention]
keep_last = 30

[encryption]
enabled = true
key_path = "/etc/backuper/master.key"

[remote]
alias = "backup_server"
remote_path = "/backups/prod-server"
EOF

# 3. Set permissions
sudo chmod 600 /etc/backuper/config.toml
sudo chown domain:domain /etc/backuper/config.toml
sudo chown domain:domain /etc/backuper/master.key

# 4. Enable timer
sudo systemctl daemon-reload
sudo systemctl enable backuper.timer
sudo systemctl start backuper.timer
```

## 🐛 Troubleshooting

### Backup Issues

#### Backup is slow or stuck

```bash
# Preview what will be backed up (dry-run)
backuper domain --config config.toml --dry-run

# Check disk I/O
iostat -x 1 10

# Review exclude patterns - too many files being processed?
# Increase exclude patterns if needed
```

#### Permission denied errors

```bash
# Backup user must read source and write to destination
sudo chown -R domain:domain /mnt/backups
sudo chmod 755 /mnt/backups

# Or run with appropriate user
sudo -u domain backuper domain --config config.toml
```

#### Out of disk space

```bash
# Check available space
df -h /mnt/backups

# Check current domain size
du -sh /mnt/backups

# Consider increasing `keep_last` to lower retention
# Or enable archival to move old backups
```

### Restore Issues

#### Restore fails with "backup file not found"

```bash
# List available backups
ls -la /mnt/backups/

# If using archive, check archive path
ls -la /mnt/backup_archive/

# Use correct path in restore command
backuper restore --file /mnt/backups/backup_2024-01-15_120000.tar.gz \
  --destination /tmp/restore
```

#### Checksum mismatch during restore

```bash
# Verify domain integrity first
backuper verify --file /mnt/backups/backup_2024-01-15_120000.tar.gz

# If mismatch, domain may be corrupted
# Re-create domain or restore from different date
backuper restore --date "2024-01-14" --archive-path /mnt/backup_archive
```

#### Decryption fails - "Unable to decrypt backup"

```bash
# Verify encryption is enabled in config
grep -A 2 "\[encryption\]" config.toml

# Verify master key exists and is readable
sudo -u domain cat /etc/backuper/master.key

# Restore with correct key path
backuper restore --file backup_encrypted.tar.gz.enc \
  --key-path /etc/backuper/master.key \
  --destination /tmp/restore
```

### Encryption Issues

#### Lost master key

**⚠️ Encrypted backups cannot be recovered without the master key.**

Prevention:
- Store master key in secure location (vault, HSM, etc.)
- Keep backup of master key in secure offline storage
- Document key location in your runbook

### Remote Backup Issues

#### SSH connection refused

```bash
# Test SSH manually
ssh -i ~/.ssh/id_ed25519_backup domain@domain.example.com "ls -la /backups"

# Check remote SSH service
ssh domain@domain.example.com "sudo systemctl status ssh"

# Check firewall
ssh domain@domain.example.com "sudo ufw status"
```

#### Remote path doesn't exist or permission denied

```bash
# Create directory on remote
ssh domain@domain.example.com "mkdir -p /backups/server-name"

# Check permissions
ssh domain@domain.example.com "ls -la /backups/"

# Make writable by domain user
ssh domain@domain.example.com "chmod 755 /backups/server-name"
```

#### Backup succeeds but no files on remote

```bash
# Check if local domain succeeded first
ls -la /mnt/backups/

# Check remote manually
ssh domain@domain.example.com "ls -la /backups/server-name/"

# View systemd logs for error details
sudo journalctl -u backuper.service -p err
```

### Systemd Issues

#### Timer never runs

```bash
# Check if timer is enabled and active
sudo systemctl status backuper.timer

# Check timer configuration
sudo systemctl cat backuper.timer

# Check next run time
systemctl list-timers backuper.timer

# Enable if not enabled
sudo systemctl enable backuper.timer
sudo systemctl start backuper.timer
```

#### Service fails silently

```bash
# Check service status
sudo systemctl status backuper.service

# View detailed logs
sudo journalctl -u backuper.service -n 100

# Run manually to see errors
sudo -u domain /usr/local/bin/backuper domain --config /etc/backuper/config.toml
```

## 🏗️ Architecture

### Project Structure

```
backuper_app/
├── backup/                      # Core backup operations
│   ├── backuper.py             # Main backup orchestration
│   ├── compression.py          # gzip/zstd compression
│   ├── encryption.py           # AES-GCM encryption
│   ├── retention.py            # Backup rotation policy
│   ├── archive.py              # Archive management
│   ├── restore.py              # Restore operations
│   ├── verify.py               # Integrity verification
│   ├── analyzer.py             # File analysis & filtering
│   ├── filter_engine.py        # Include/exclude patterns
│   ├── manifest.py             # Backup metadata
│   ├── initializer.py          # Config initialization
│   └── remote.py               # SSH remote sync
├── config/
│   └── config.py               # TOML config parsing
├── cli.py                       # CLI argument parsing
├── main.py                      # Entry point
├── dto.py                       # Data transfer objects
├── exception.py                 # Custom exceptions
└── utils/
    ├── logger.py               # Logging (stdout)
    ├── checksum.py             # SHA256 hashing
    ├── capacity.py             # Size calculations
    ├── archive_resolver.py     # Archive path resolution
    └── temporary.py            # Temporary workspace
```

### Backup Workflow

```
1. Load Config (TOML)
   ↓
2. Analyze Source (filter include/exclude)
   ↓
3. Create Compressed Archive (gzip/zstd)
   ↓
4. Encrypt (if enabled)
   ↓
5. Generate Checksum
   ↓
6. Apply Retention Policy
   ├─ Keep last N backups
   ├─ Archive or delete old backups
   └─ Update manifest
   ↓
7. Sync to Remote (if configured)
   └─ SSH push to remote_path
```

### Restore Workflow

```
1. Receive Restore Request (file/date)
   ↓
2. Locate Backup File
   ├─ Check local destination
   └─ Check archive if needed
   ↓
3. Validate Checksum
   ↓
4. Decrypt (if encrypted, requires key)
   ↓
5. Extract to Destination
   └─ Restore permissions & metadata
```

### File Format

**Backup File Naming:** `backup_YYYY-MM-DD_HHMMSS.tar.{gz|zst}[.enc]`

**Manifest File:** `.backup_manifest` (JSON metadata)

**Checksum File:** `.backup_checksum` (SHA256 hash)

## 💡 Best Practices

1. **Always dry-run first:** `backuper backup --config config.toml --dry-run`
2. **Test restore:** Periodically test restoring from backups to verify integrity
3. **Encrypt sensitive data:** Enable encryption for confidential backups
4. **Use retention policy:** Keep last N backups to save storage and manage rotation
5. **Archive instead of delete:** Enable archival to preserve backups for longer periods
6. **Monitor logs:** Regular check `journalctl` output for errors or anomalies
7. **Secure master key:** Store encryption key securely, consider using a vault
8. **SSH key management:** Use SSH keys instead of passwords, restrict key permissions
9. **Test remote sync:** Verify SSH connection works before relying on remote backup
10. **Document config:** Add comments in TOML config explaining each backup job

## 📊 Performance Tuning

- **Compression ratio:** zstd > gzip (storage) but gzip > zstd (speed)
- **Retention policy:** Lower `keep_last` to save disk space; higher for safety
- **Filtering:** Tight `exclude` patterns reduce processing time
- **Encryption:** Adds ~5-10% overhead; acceptable for most scenarios
- **Systemd timing:** Avoid peak hours; schedule backups during low-usage periods

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Resources

- **GitHub:** [Finsa-SC/backup-service](https://github.com/Finsa-SC/File_Backuper)
- **PyPI:** [file-backuper](https://pypi.org/project/file-backuper/)
- **Issues:** [GitHub Issues](https://github.com/Finsa-SC/File_Backuper/issues)

---

**Made with ❤️ for reliable backups**