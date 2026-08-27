from backuper_app.exception import BackuperError

def validate_compression(compression: str, compression_input: str = None):
    if compression:
        return compression
    else:
        raise BackuperError(f"Invalid compression type: {compression or compression_input}")
