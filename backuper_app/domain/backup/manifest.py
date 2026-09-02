import json
from importlib.metadata import files
from pathlib import Path
from datetime import datetime
from typing import Any

#Return temporary directory path
def make_manifest(
        workspace_path: Path,
        data: dict[str, Any]
    ) -> Path:

    manifest_file = workspace_path / "manifest.json"

    with manifest_file.open('w')as man_file:
        json.dump(data, man_file, indent=4)

    return Path(manifest_file)

def create_manifest_data(
        workspace_path: Path,
        backup_name : str,
        target_path : Path,
        include     : list[str],
        exclude     : list[str],
        compression : str,
        link_mode   : str,
        file_list   : list[Path],
):
    files_str = [str(path.relative_to(target_path)) for path in file_list]
    manifest_data = dict(
        backup_name = backup_name,
        created_at  = datetime.now().replace(microsecond= 0).isoformat() + "Z",
        target      = str(target_path),
        include     = include,
        exclude     = exclude,
        compression = compression,
        link_mode   = link_mode,
        files       = files_str,
    )

    return make_manifest(workspace_path, manifest_data)
