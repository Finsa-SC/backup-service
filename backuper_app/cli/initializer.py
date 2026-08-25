from backuper_app.application.initializer import Initializer
from backuper_app.infrastructure import get_logger

logger = get_logger(__name__)

def run_init(request):
    init = Initializer(
        request
    )

    config_path = init.make_init()
    logger.info(f"Initial config has been created: {config_path}")
    logger.info("Edit the file before running `backuper domain`.")
