from tempfile import TemporaryDirectory
from pathlib import Path
from backuper_app.exception import BackuperError

class TemporaryWorkspace:
    def __init__(self, parent_name: str):
        self._temp_dir = TemporaryDirectory(
            prefix=f"{parent_name}-",
            delete=False
        )
        self._root = Path(self._temp_dir.name)

        self.workspaces: dict = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean_up()
        return False

    def _create_temp_workspace(self, workspace_name: str) -> Path:
        temp_workspace =  Path(self._root / workspace_name)
        temp_workspace.mkdir(parents=True, exist_ok=True)

        return temp_workspace

    def new_workpace(self, workspace: str) -> Path:
        workspace_path = self._create_temp_workspace(workspace)
        self.workspaces[workspace] = workspace_path

        return workspace_path

    def get_workspace_path(self, workspace):
        found_workspace = self.workspaces.get(workspace, None)

        if found_workspace:
            return found_workspace
        else:
            raise BackuperError(f"Workpace not found for {workspace}")

    def clean_up(self):
        self._temp_dir.cleanup()