import json
from pathlib import Path
from datetime import datetime
import tempfile

def make_temp_manifest(backup_name: str, data: dict) -> Path:
    with tempfile.NamedTemporaryFile(mode="w+", prefix=f".{backup_name}", suffix=".json", delete=False) as temp_file:
        json.dump(data, temp_file, indent=4)
        return Path(temp_file.name)

def create_manifest_data(
        backup_name: str,
        target_path: Path,
        include: list[str],
        exclude: list[str],
):
    manifest_data = dict(
        backup_name=backup_name,
        created_at=datetime.now().replace(microsecond=0).isoformat() + "Z",
        target=str(target_path),
        include=include,
        exclude=exclude
    )

    return make_temp_manifest(backup_name, manifest_data)

if __name__ == "__main__":
    path = create_manifest_data("agus", Path("/home"), include=[".gitignore"], exclude=[".venv"])
    print(path)
    with path.open("r") as file:
        print(file.read())
    path.unlink()
