from backuper_app.dto import RemoteConfig, ValidateRequest
from backuper_app.validation import validate_path, validate_compression, validate_ssh_config

class Validate:
    def __init__(self, request: ValidateRequest):
        self.target_path        = request.target_path
        self.destination_path   = request.destination_path
        self.compression_type   = request.compression_type

        self.archive_enabled    = request.archive_enabled
        self.archive_path       = request.archive_path

        self.encryption_enabled = request.encryption_enabled
        self.key_path = request.key_path

        self.remote_config: RemoteConfig = request.remote_config

    def validate_config(self) -> None:
        validate_path(
            self.target_path,
            self.destination_path,
        )

        validate_compression(self.compression_type)

        if self.archive_enabled:
            validate_path(self.archive_path)

        if self.encryption_enabled:
            validate_path(self.key_path)

        if self.remote_config.enabled:
            validate_ssh_config(
                hostname    = self.remote_config.host,
                username    = self.remote_config.user,
                port        = self.remote_config.port,
                remote_path = self.remote_config.remote_path,
            )