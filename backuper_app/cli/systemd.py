from pathlib import Path

from backuper_app.application import Systemd
from backuper_app.dto import SystemdRequest
from backuper_app.infrastructure import get_logger

logger = get_logger(__name__)

def run_systemd(jobs: list[str], destination: Path) -> None:
    logger.info(f"Generating {jobs} units file")
    systemd_request = SystemdRequest(
        jobs=jobs,
        destination=destination,
    )
    systemd = Systemd(systemd_request)

    systemd.generate_units()

    logger.info(f"Units has been generate in {destination}")