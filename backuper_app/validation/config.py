from backuper_app.exception import ConfigurationError

PERMISSION_MODE = [
    "0", "1", "2", "3",
    "4", "5", "6", "7",
]

def get_validate_file_mode(mode) -> int | None:
    if not mode:
        return None

    if not isinstance(mode, str):
        raise ConfigurationError(f"Invalid file mode type: got {type(mode)}, expected 'str'")

    len_mode = len(mode)
    if not len_mode == 3:
        raise ConfigurationError(f"Invalid len of file mode: got {len_mode} len, expected 3 len")

    for perm in mode:
        if perm not in PERMISSION_MODE:
            raise ConfigurationError(f"Invalid file mode: got '{mode}', expected three octal digits (0-7), e.g. 600")

    try:
        return int(mode, 8)
    except Exception:
        raise ConfigurationError(f"Invalid permission, got {mode}. Expected like 640")