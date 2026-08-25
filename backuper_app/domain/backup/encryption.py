import os, hashlib, struct
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pathlib import Path
from backuper_app.exception import EncryptionError, BackuperError
from backuper_app.infrastructure import TemporaryWorkspace
from backuper_app.validation import validate_encrypted_file_not_malformed, validate_encryption_version

CHUNK_SIZE = 8 * 1024 * 1024

class Encryption:
    def __init__(self, key_path: Path):
        self.__key_path = key_path
        self.master_key = key_path
        self.temporary_decrypt_file = None

    @property
    def master_key(self):
        return "***"

    @master_key.setter
    def master_key(self, value: Path):
        try:
            with value.open('rb') as file:
                data = file.read()
        except PermissionError as e:
            raise BackuperError("Unable to read master key") from e
        if len(data) <= 0:
            raise BackuperError("Master key is empty, please provide a valid key")

        self.__master_key = self._decode_to_32_byte(data)

    @staticmethod
    def _decode_to_32_byte(data_key):
        return hashlib.sha256(data_key).digest()

    @staticmethod
    def _encrypt(aesgcm, file_in, file_out):
        file_out.write(struct.pack("B", 1))

        while chunk := file_in.read(CHUNK_SIZE):
            nonce = os.urandom(12)
            ciphertext = aesgcm.encrypt(nonce, chunk, None)
            ciphertext_size = len(ciphertext)
            ciphertext_size_bytes = struct.pack(">Q", ciphertext_size)

            file_out.write(ciphertext_size_bytes)
            file_out.write(nonce)
            file_out.write(ciphertext)

    @staticmethod
    def _decrypt(aesgcm, file_in, file_out):
        # Version verification
        version_bytes = file_in.read(1)
        version = struct.unpack("B", version_bytes)[0]
        validate_encryption_version(version)

        while True:
            # Get chunk size
            ciphertext_size_bytes = file_in.read(8)
            if not ciphertext_size_bytes:
                break
            ciphertext_size = struct.unpack(">Q", ciphertext_size_bytes)[0]

            nonce = file_in.read(12)
            ciphertext = file_in.read(ciphertext_size)

            plain_text = aesgcm.decrypt(nonce, ciphertext, None)
            file_out.write(plain_text)

    def encrypt_file(self, file_path: Path) -> Path:
        encrypted_path = file_path.with_suffix(file_path.suffix + ".enc")
        aesgcm = AESGCM(self.__master_key)

        with (
            file_path.open('rb') as file_in,
            encrypted_path.open('wb') as file_out
        ):
            self._encrypt(aesgcm, file_in, file_out)

        # Cleanup plain domain
        if encrypted_path.exists(follow_symlinks=True):
            file_path.unlink(missing_ok=True)

        return encrypted_path

    def decrypt_file(self, enc_file_path: Path, workspace: TemporaryWorkspace) -> Path:
        dir_path = workspace.new_workpace("decrypt_file")

        file_name = enc_file_path.with_name(enc_file_path.name.removesuffix(".enc"))
        decrypted_file = dir_path / file_name.name

        aesgcm = AESGCM(self.__master_key)

        # Validate encrypted domain structure
        validate_encrypted_file_not_malformed(enc_file_path)

        with (
            enc_file_path.open('rb') as file_in,
            decrypted_file.open('wb') as file_out
        ):
            try:
                self._decrypt(aesgcm, file_in, file_out)
            except InvalidTag:
                raise EncryptionError("Unable to decrypt domain: invalid key or corrupted domain")

        return Path(decrypted_file)

# # # Public function

def is_encrypted_file(file_path: Path) -> bool:
    return file_path.suffix == ".enc"