import os
import hashlib
import struct

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pathlib import Path
from backuper_app.exception import EncryptionError, BackuperError

MIN_ENCRYPTED_SIZE = 12 + 16
CHUNK_SIZE = 8 * 1024 * 1024

class Encryption:
    def __init__(self, key_path: Path):
        self.__key_path = key_path
        self.master_key = key_path

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

    def _encrypt(self, file_in, file_out):
        aesgcm = AESGCM(self.__master_key)

        file_out.write(struct.pack("B", 1))

        while chunk := file_in.read(CHUNK_SIZE):
            nonce = os.urandom(12)
            ciphertext = aesgcm.encrypt(nonce, chunk, None)
            ciphertext_size = len(ciphertext)
            ciphertext_size_bytes = struct.pack(">Q", ciphertext_size)

            file_out.write(ciphertext_size_bytes)
            file_out.write(nonce)
            file_out.write(ciphertext)

    def encrypt_file(self, file_path: Path) -> Path:
        encrypted_path = file_path.with_suffix(file_path.suffix + ".enc")

        with (
            file_path.open('rb') as file_in,
            encrypted_path.open('wb') as file_out
        ):
            self._encrypt(file_in, file_out)

        # Cleanup plain backup
        if encrypted_path.exists(follow_symlinks=True):
            file_path.unlink(missing_ok=True)

        return encrypted_path

    def decrypt_file(self, enc_file_path: Path) -> Path:
        decrypted_file = enc_file_path.with_name(enc_file_path.name.removesuffix(".enc"))

        aesgcm = AESGCM(self.__master_key)

        # Validate encrypted backup structure
        if enc_file_path.stat().st_size < MIN_ENCRYPTED_SIZE:
            raise EncryptionError("Malformed encryption backup")

        with enc_file_path.open('rb') as file_in:
            file_content = file_in.read()

        nonce = file_content[:12]
        ciphertext = file_content[12:]

        try:
            data_text = aesgcm.decrypt(nonce, ciphertext, None)
        except InvalidTag:
            raise EncryptionError("Unable to decrypt backup: invalid key or corrupted backup")

        with decrypted_file.open('wb') as file_out:
            file_out.write(data_text)

        # Cleanup encrypted backup
        if decrypted_file.exists(follow_symlinks=True):
            enc_file_path.unlink(missing_ok=True)

        return decrypted_file


# Public function

def is_encrypted_file(file_path: Path) -> bool:
    return file_path.suffix == ".enc"

if __name__ == "__main__":
    my_key = Path("/etc/backuper/master.key")
    my_file = Path("/home/silence-suzuka/backup_test/playground_20260807_140704.tar.gz")
    my_enc = my_file.with_suffix(my_file.suffix + ".enc")
    enc = Encryption(my_key)

    # enc.encrypt_file(my_file)
    enc.decrypt_file(my_enc)