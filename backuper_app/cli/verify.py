from backuper_app.application.verify import verify_backup
from backuper_app.infrastructure import get_file_by_path_or_date, get_logger
from backuper_app.validation import is_valid_input_archive

logger = get_logger(__name__)

def run_verify(request):
    if is_valid_input_archive(file=request.file_path, date=request.date, archive_path=request.archive_path):
        file_path = get_file_by_path_or_date(request.file_path, request.archive_path, request.date)
        is_valid = verify_backup(
            file_path=file_path,
            key_path=request.key_path
        )
        if is_valid:
            logger.info(f"Archive verification passed for {file_path.name}")
