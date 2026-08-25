from tempfile import TemporaryDirectory
from pathlib import Path
from backuper_app.exception import BackuperError

class TemporaryWorkspace:
    def __init__(self, parent_name: str):
        self.parent_name = parent_name
        self._temp_dir = None
        self._root = None

        self.workspaces: dict = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean_up()
        return False

    def _create_temp_root_workspace(self) -> TemporaryDirectory:
        return TemporaryDirectory(
            prefix=f"{self.parent_name}-",
            delete=False
        )

    def _create_temp_workspace(self, workspace_name: str) -> Path:
        temp_workspace = self._root / workspace_name
        temp_workspace.mkdir(parents=True, exist_ok=True)

        return temp_workspace

    def new_workpace(self, workspace: str) -> Path:
        if not self._temp_dir:
            self._temp_dir = self._create_temp_root_workspace()
            self._root = Path(self._temp_dir.name)

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
        if self._temp_dir:
            self._temp_dir.cleanup()