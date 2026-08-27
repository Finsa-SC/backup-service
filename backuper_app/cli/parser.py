import argparse
from importlib.metadata import version
from pathlib import Path

from backuper_app.config import Config

VERSION = version("file-backuper")

def get_arg_parse():
    parser = argparse.ArgumentParser(
        prog="backuper",
        description="Backup Service",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}"
    )

    subparser = parser.add_subparsers(
        dest="command",
        required=True,
    )

    ### Backup Mode
    backup_mode = subparser.add_parser(
        name="backup",
        help="Create new backup",
        description="Create new backup",
    )
    backup_mode.add_argument(
        "--config",
        required=True,
        type=Path,
        default=None,
        help="Path to Configuration target",
    )
    backup_mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Trial without actually taking action"
    )

    ### Restore Mode
    restore_mode = subparser.add_parser(
        name="restore",
        help="Extract archive backup",
        description="Extract archive backup",
    )
    restore_mode.add_argument(
        "--file",
        type=Path,
        default=None,
        help="File path you want to restore",
    )
    restore_mode.add_argument(
        "--date",
        type=str,
        default=None,
        help="Date archive you want to restore(require --archive-path)",
    )
    restore_mode.add_argument(
        "--destination",
        type=Path,
        default=Path("/tmp/backup_restore"),
        help="Path to extract directory destination you want, default is /tmp/backup_restore",
    )
    restore_mode.add_argument(
        "--archive-path",
        help="Path to your archive directory to find file to be extract",
    )
    restore_mode.add_argument(
        "--key-path",
        type=Path,
        default=None,
        help="Path to your master code to open encryption backup"
    )

    ### Verify
    verify_mode = subparser.add_parser(
        name="verify",
        help="verify backup data with checksum",
        description="verify backup data with checksum",
    )
    verify_mode.add_argument(
        "--file",
        type=Path,
        default=None,
        help="File path you want to verify",
    )
    verify_mode.add_argument(
        "--date",
        type=str,
        default=None,
        help="Date archive you want to verify(require --archive-path)",
    )
    verify_mode.add_argument(
        "--archive-path",
        type=Path,
        default=None,
        help="Path to your archive directory to find file to be verify",
    )
    verify_mode.add_argument(
        "--key-path",
        type=Path,
        default=None,
        help="Path to your master key file",
    )

    ### Init
    init_mode = subparser.add_parser(
        name="init",
        help="Create an initial configuration file",
        description="Create an initial configuration file from the default template.",
    )
    init_mode.add_argument(
        "config",
        type=Path,
        nargs="?",
        default=None,
        help="Path to the configuration file (default: /etc/backuper/config.toml).",
    )
    init_mode.add_argument(
        "-t",
        "--target",
        type=Path,
        default=None,
        help="Path to the backup target directory.",
    )
    init_mode.add_argument(
        "-d",
        "--destination",
        type=Path,
        default=None,
        help="Path to the backup destination directory.",
    )
    init_mode.add_argument(
        "-r",
        "--retention",
        type=int,
        default=None,
        help="Number of backups to retain.",
    )
    init_mode.add_argument(
        "-c",
        "--compression",
        choices=["gzip", "zstd"],
        default="zstd",
        help="Compression method.",
    )
    init_mode.add_argument(
        "-l",
        "--link-mode",
        choices=["ignore", "follow", "preserve"],
        default="preserve",
        help="How symbolic links are handled.",
    )
    init_mode.add_argument(
        "-a",
        "--archive-path",
        default=None,
        help="Path to archive backup",
    )
    init_mode.add_argument(
        "--key-path",
        default=None,
        help="Path to master key to open encrypted backup"
    )

    # Remote
    init_mode.add_argument(
        "--remote-host",
        default=None,
        help="Remote SSH host.",
    )
    init_mode.add_argument(
        "--remote-user",
        default=None,
        help="Remote SSH username.",
    )
    init_mode.add_argument(
        "--remote-port",
        type=int,
        default=22,
        help="Remote SSH port (default: 22).",
    )
    init_mode.add_argument(
        "--remote-identity-file",
        default=None,
        help="Path to SSH identity file.",
    )
    init_mode.add_argument(
        "--remote-path",
        default=None,
        help="Path to store backups on the remote server.",
    )
    init_mode.add_argument(
        "--remote-alias",
        default=None,
        help="SSH config alias.",
    )

    # Validate config
    validate_mode = subparser.add_parser(
        name="validate",
        help="validate configuration",
        description="validate configuration"
    )
    validate_mode.add_argument(
        "--config",
        type=Path,
        default=None,
        required=True,
        help="Path to your config file you want to validate."
    )

    return parser.parse_args()

def load_config(config_path: Path):
    backup_config = Config(config_path)
    return backup_config.set_config()