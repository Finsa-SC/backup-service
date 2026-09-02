from pathlib import Path

from backuper_app.dto import SystemdRequest
from backuper_app.exception import BackuperError

class Systemd:
    PROJECT_ROOT_PATH        = Path(__file__).parents[1]
    SYSTEMD_TEMPLATES_PATH   = Path(PROJECT_ROOT_PATH / "templates" / "systemd")

    SERVICE_UNIT_BACKUP_PATH = Path(SYSTEMD_TEMPLATES_PATH / "backuper_backup.service")
    TIMER_UNIT_BACKUP_PATH   = Path(SYSTEMD_TEMPLATES_PATH / "backuper_backup.timer")

    SERVICE_UNIT_RESTORE_PATH = Path(SYSTEMD_TEMPLATES_PATH / "backuper_backup.service")
    TIMER_UNIT_RESTORE_PATH   = Path(SYSTEMD_TEMPLATES_PATH / "backuper_backup.timer")

    def __init__(self, request: SystemdRequest):
        self.destination = request.destination
        self.jobs = request.jobs

    def generate_unit_backup(self, destination: Path) -> None:
        self.SERVICE_UNIT_RESTORE_PATH.copy_into(destination)
        self.TIMER_UNIT_RESTORE_PATH.copy_into(destination)

    def generate_unit_test_restore(self, destination: Path) -> None:
        self.SERVICE_UNIT_BACKUP_PATH.copy_into(destination)
        self.TIMER_UNIT_BACKUP_PATH.copy_into(destination)

    def generate_units(self) -> None:
        if "backup" in self.jobs:
            self.generate_unit_backup(self.destination)
        if "test-restore" in self.jobs:
            self.generate_unit_test_restore(self.destination)