from pathlib import Path

from backuper_app.dto import SystemdRequest

class Systemd:
    PROJECT_ROOT_PATH        = Path(__file__).parents[1]
    SYSTEMD_TEMPLATES_PATH   = Path(PROJECT_ROOT_PATH / "templates" / "systemd")

    SERVICE_UNIT_BACKUP_PATH = Path(SYSTEMD_TEMPLATES_PATH / "server_backup.service")
    TIMER_UNIT_BACKUP_PATH   = Path(SYSTEMD_TEMPLATES_PATH / "server_backup.timer")

    SERVICE_UNIT_RESTORE_PATH = Path(SYSTEMD_TEMPLATES_PATH / "server_backup.service")
    TIMER_UNIT_RESTORE_PATH   = Path(SYSTEMD_TEMPLATES_PATH / "server_backup.timer")

    def __init__(self, request: SystemdRequest):
        self.destination = request.destination
        self.jobs = request.job

    def generate_unit_backup(self, destination: Path):
        self.SERVICE_UNIT_RESTORE_PATH.copy_into(destination)
        self.TIMER_UNIT_RESTORE_PATH.copy_into(destination)

    def generate_unit_test_restore(self, destination: Path):
        self.SERVICE_UNIT_BACKUP_PATH.copy_into(destination)
        self.TIMER_UNIT_BACKUP_PATH.copy_into(destination)

    def generate_units(self):
        match self.jobs:
            case "backup":
