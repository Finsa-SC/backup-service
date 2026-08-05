import json
from pathlib import Path
from datetime import datetime
from tempfile import TemporaryDirectory

#Return temporary directory path
def make_temp_manifest(backup_name: str, data: dict) -> Path:
    with TemporaryDirectory(delete=False) as temp_dir:
        dir_path = Path(temp_dir)

        backuper_path = Path(dir_path / ".manifest")
        backuper_path.mkdir(exist_ok=True, parents=True)

        manifest_file = backuper_path / "manifest.json"
        with manifest_file.open('w')as man_file:
            json.dump(data, man_file, indent=4)
        return Path(dir_path)

def create_manifest_data(
        backup_name: str,
        target_path: Path,
        include: list[str],
        exclude: list[str],
        compression: str,
        link_mode: str,
):
    manifest_data = dict(
        backup_name=backup_name,
        created_at=datetime.now().replace(microsecond=0).isoformat() + "Z",
        target=str(target_path),
        include=include,
        exclude=exclude,
        compression=compression,
        link_mode=link_mode,
    )

    return make_temp_manifest(backup_name, manifest_data)

if __name__ == "__main__":
    path = create_manifest_data("agus", Path("/home"), include=[".gitignore"], exclude=[".venv"])
    print(path)
    with path.open("r") as file:
        print(file.read())
    path.unlink()
