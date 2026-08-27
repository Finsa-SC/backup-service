from backuper_app.application.validate import Validate
from backuper_app.dto import RemoteConfig, ValidateRequest
from backuper_app.infrastructure import get_logger

logger = get_logger(__name__)

def run_validate(config):
    remote_config = RemoteConfig(
        enabled=config.remote_enabled,
        host=config.remote_host,
        user=config.remote_user,
        port=config.remote_port,
        identity_file=config.identity_file,
        remote_path=config.remote_path,
        alias=config.alias,
    )
    validate_request = ValidateRequest(
        target_path=config.target,
        destination_path=config.destination,
        compression_type=config.compression,

        archive_enabled=config.archive_enabled,
        archive_path=config.archive_path,

        encryption_enabled=config.encryption_enabled,
        key_path=config.key_path,

        remote_config=remote_config
    )
    validate = Validate(
        validate_request
    )
    validate.validate_config()

    logger.info("Configuration is valid")