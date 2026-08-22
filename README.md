# File Backuper

[![Release](https://img.shields.io/badge/release-v1.2.0-blue)](https://github.com/Finsa-SC/backup-service/releases/tag/v1.2.0)
[![Python](https://img.shields.io/badge/python-3.14%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A powerful, modular CLI backup utility for creating, restoring, and verifying file backups with advanced features like compression, retention policies, and data integrity verification.

> **Latest Release:** v1.2.0 — Now supports setting default file config during initialization!

## Features

- **Flexible Backup Creation** - Backup files and directories with include/exclude filtering
- **Multiple Compression Methods** - Support for gzip and zstd compression algorithms
- **Retention Policies** - Automatically manage backup rotation and keep only the last N backups
- **Data Integrity** - Built-in checksum verification for backup validation
- **Restore Capabilities** - Extract backups by file path or date with integrity checking
- **Symbolic Link Handling** - Choose how to handle symlinks (ignore, follow, or preserve)
- **Archive Support** - Automatically archive expired backups to a separate location
- **Dry-Run Mode** - Preview backup operations before execution
- **Configuration-Based** - TOML-based configuration for easy management
- **Detailed Logging** - Comprehensive logging for monitoring and troubleshooting

## What's New in v1.2.0

- ✨ **Default File Config in Init** - Set default configuration file during initialization
- 🔧 Improved configuration workflow
- 📋 [Full Changelog](https://github.com/Finsa-SC/backup-service/releases/tag/v1.2.0)

## Installation

### Requirements
- Python >= 3.14
- pip or uv

### From GitHub Releases

Download and install the latest release:

```bash
# Extract the release
unzip file-backuper-1.2.0.tar.gz
cd backup-service

# Install
pip install .
```

### From Source

```bash
git clone https://github.com/Finsa-SC/backup-service.git
cd backup-service
pip install -e .
```

### Using uv (recommended)
```bash
uv pip install -e .
```

This creates the `backuper` command available in your PATH.

## Quick Start

### 1. Initialize Configuration

```bash
backuper init --target /path/to/backup --destination /path/to/backups
```

Or with all options:
```bash
backuper init /etc/backuper/config.toml \
  --target /home/user/documents \
  --destination /mnt/backups \
  --retention 5 \
  --compression zstd \
  --link-mode preserve
```

### 2. Create a Backup

```bash
backuper backup --config /etc/backuper/config.toml
```

Preview before executing:
```bash
backuper backup --config /etc/backuper/config.toml --dry-run
```

### 3. Restore from Backup

Restore a specific file:
```bash
backuper restore --file /path/to/backup/file.tar.gz --destination /tmp/restore
```

Restore a backup by date:
```bash
backuper restore --date "2024-01-15" --archive-path /mnt/backups --destination /tmp/restore
```

### 4. Verify Backup Integrity

Verify a specific backup file:
```bash
backuper verify --file /path/to/backup/file.tar.gz
```

Verify a backup by date:
```bash
backuper verify --date "2024-01-15" --archive-path /mnt/backups
```

## Configuration

Configuration is managed through a TOML file (default: `config.toml`).

### Example Configuration

```toml
[backup]
backup_name = "my_backup"
target = "/home/user/documents"
destination = "/mnt/backups"
compression = "zstd"  # or "gzip"
keep_last = 5
link_mode = "preserve"  # options: ignore, follow, preserve
archive_enable = true
archive_path = "/mnt/backups/archive"

[filter]
include = ["*.txt", "*.pdf"]
exclude = ["*.tmp", "*.cache"]
```

### Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `backup_name` | string | Name identifier for this backup job |
| `target` | path | Source directory/file to backup |
| `destination_path` | path | Directory where backups are stored |
| `compression` | string | Compression method: `gzip` or `zstd` |
| `keep_last` | integer | Number of backups to retain (0 = keep all) |
| `link_mode` | string | Symlink handling: `ignore`, `follow`, or `preserve` |
| `archive_enabled` | boolean | Archive expired backups instead of deleting |
| `archive_path` | path | Directory for archived backups (if enabled) |
| `include` | array | File patterns to include (optional) |
| `exclude` | array | File patterns to exclude (optional) |

## Command Reference

### backup
Create a new backup with retention and archival support.

```bash
backuper backup --config CONFIG_PATH [--dry-run]
```

**Options:**
- `--config CONFIG_PATH` (required): Path to configuration file
- `--dry-run`: Preview without actually creating backup

### restore
Extract backup data by file path or date with integrity verification.

```bash
backuper restore [--file FILE_PATH | --date DATE] --destination DEST_PATH [--archive-path ARCHIVE_PATH]
```

**Options:**
- `--file FILE_PATH`: Path to specific backup file to restore
- `--date DATE`: Date of backup to restore (requires `--archive-path`)
- `--destination DEST_PATH`: Where to extract files (default: `/tmp/backup_restore`)
- `--archive-path ARCHIVE_PATH`: Path to archive directory (required when using `--date`)

### verify
Verify backup integrity using stored checksums.

```bash
backuper verify [--file FILE_PATH | --date DATE] [--archive-path ARCHIVE_PATH]
```

**Options:**
- `--file FILE_PATH`: Path to backup file to verify
- `--date DATE`: Date of backup to verify (requires `--archive-path`)
- `--archive-path ARCHIVE_PATH`: Path to archive directory

### init
Create an initial configuration file from template.

```bash
backuper init [CONFIG_PATH] [--target TARGET] [--destination DEST] [--retention N] [--compression METHOD] [--link-mode MODE]
```

**Options:**
- `CONFIG_PATH`: Configuration file path (default: `/etc/backuper/config.toml`)
- `--target`: Source directory to backup
- `--destination`: Backup destination directory
- `--retention`: Number of backups to keep
- `--compression`: Compression method (`gzip` or `zstd`)
- `--link-mode`: Symlink handling mode

## Architecture

```
backuper_app/
├── backup/              # Core backup functionality
│   ├── backuper.py     # Main backup engine
│   ├── compression.py  # Compression handling
│   ├── retention.py    # Backup rotation & cleanup
│   ├── archive.py      # Archive management
│   ├── restore.py      # Restore operations
│   ├── verify.py       # Integrity verification
│   ├── analyzer.py     # File analysis & filtering
│   ├── filter_engine.py # Include/exclude filtering
│   ├── manifest.py     # Backup metadata
│   └── initializer.py  # Config initialization
├── config/             # Configuration handling
│   └── config.py       # Config parsing & validation
├── utils/              # Utility functions
│   ├── checksum.py     # Hash & verification
│   ├── logger.py       # Logging setup
│   ├── capacity.py     # Size calculations
│   └── archive_resolver.py  # Archive path resolution
└── main.py             # CLI entry point
```

## Workflow

### Backup Workflow
1. Load configuration from TOML file
2. Analyze source directory with filtering
3. Create compressed archive (gzip or zstd)
4. Generate checksum for integrity verification
5. Check retention policy
6. Archive or delete old backups based on retention settings

### Restore Workflow
1. Validate backup file checksum
2. Extract archive to destination
3. Restore file permissions and metadata

### Verification Workflow
1. Calculate checksum of backup file
2. Compare with stored checksum
3. Report integrity status

## Examples

### Backup with retention

```bash
# Create initial config
backuper init my_backup.toml \
  --target /home/user/documents \
  --destination /mnt/backups \
  --retention 7 \
  --compression zstd

# Create backup (keeps last 7 backups)
backuper backup --config my_backup.toml
```

### Backup with filtering

```toml
[backup]
backup_name = "selective_backup"
target = "/home/user"
destination = "/mnt/backups"
compression = "zstd"

[filter]
include = ["*.txt", "*.pdf", "Documents/**"]
exclude = ["*.tmp", ".git/**", "node_modules/**"]
```

### Scheduled backups with systemd

```ini
# /etc/systemd/system/backuper.service
[Unit]
Description=File Backuper Service
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backuper backup --config /etc/backuper/config.toml
User=backup
StandardOutput=journal

# /etc/systemd/system/backuper.timer
[Unit]
Description=Daily Backup Timer
Requires=backuper.service

[Timer]
OnCalendar=daily
OnCalendar=00:02
Persistent=true

[Install]
WantedBy=timers.target
```

## Error Handling

The tool provides clear error messages for common issues:

- **Invalid config**: Check TOML syntax and required fields
- **Permission denied**: Verify read/write permissions on source and destination
- **Checksum mismatch**: Backup may be corrupted, re-create backup
- **Insufficient space**: Ensure destination has enough free space

## Performance Notes

- **Compression**: zstd typically offers better compression ratios than gzip
- **Retention**: Archiving is preferred over deletion for safety
- **Symbolic links**: Use `preserve` mode to maintain symlink structure
- **Large files**: Dry-run mode helps preview operations before execution

## Development

### Project Structure
- Modular design with clear separation of concerns
- Type hints for better IDE support
- Comprehensive logging throughout
- Exception handling with custom `BackuperError`

### Running Tests
```bash
python -m pytest test/
```

## License

[Add your license here]

## Contributing

Contributions are welcome! Please ensure:
- Code follows the existing style
- New features include tests
- Documentation is updated
- Commit messages are descriptive

## Support & Resources

- 📖 [Documentation](https://github.com/Finsa-SC/backup-service)
- 🐛 [Issue Tracker](https://github.com/Finsa-SC/backup-service/issues)
- 📝 [Releases](https://github.com/Finsa-SC/backup-service/releases)
- 💬 For questions, open an issue on GitHub

## Troubleshooting

**Backup stuck or slow?**
- Use `--dry-run` to check what's being processed
- Check exclude patterns if too many files
- Monitor disk I/O with `iostat`

**Restore fails?**
- Verify backup file exists and is accessible
- Check checksum: `backuper verify --file <backup>`
- Ensure destination has write permissions

**Config errors?**
- Validate TOML syntax at https://www.toml-lint.com/
- Ensure all paths are absolute and exist
- Check file permissions for config file

## Release History

### v1.2.0 (Current)
**Released:** Recently
- ✨ Feature to set default file config in init
- 🔧 Enhanced configuration initialization workflow
- 📚 Improved documentation

[View Release](https://github.com/Finsa-SC/backup-service/releases/tag/v1.2.0)

### v1.0.1
- Previous stable release

### v1.0.0
- Initial release

---

## Version Info

**Current version:** 1.2.0  
**Python requirement:** >= 3.14  
**Latest release:** [v1.2.0](https://github.com/Finsa-SC/backup-service/releases/tag/v1.2.0)
