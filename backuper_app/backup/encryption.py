import os
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pathlib import Path

class Encryption:
    def __init__(self, key_path: Path):
        self.__key_path = key_path
        self.master_key = key_path

    @property
    def master_key(self):
        return "***"

    @master_key.setter
    def master_key(self, value: Path):
        with value.open('rb') as file:
            data = file.read()
            self.__master_key = self._decode_to_32_byte(data)

    @staticmethod
    def _decode_to_32_byte(data_key):
        return hashlib.sha256(data_key).digest()

    @staticmethod
    def is_encrypted_file(file_path: Path) -> bool:
        return ".enc" in file_path.suffixes

    def encrypt_file(self, file_path: Path) -> Path:
        encrypted_path = file_path.with_suffix(file_path.suffix + ".enc")
        aesgcm = AESGCM(self.__master_key)
        nonce = os.urandom(12)

        with file_path.open('rb') as file_in:
            file_content = file_in.read()

        ciphertext = aesgcm.encrypt(nonce, file_content, None)

        with encrypted_path.open('wb') as file_out:
            file_out.write(nonce + ciphertext)

        # Cleanup plain backup
        if encrypted_path.exists(follow_symlinks=True):
            file_path.unlink(missing_ok=True)

        return encrypted_path

    def decrypt_file(self, enc_file_path: Path) -> Path:
        decrypted_file = enc_file_path.with_name(enc_file_path.name.removesuffix(".enc"))

        aesgcm = AESGCM(self.__master_key)

        with enc_file_path.open('rb') as file_in:
            file_content = file_in.read()

        nonce = file_content[:12]
        ciphertext = file_content[12:]

        data_text = aesgcm.decrypt(nonce, ciphertext, None)
        with decrypted_file.open('wb') as file_out:
            file_out.write(data_text)

        # Cleanup encrypted backup
        if decrypted_file.exists(follow_symlinks=True):
            enc_file_path.unlink(missing_ok=True)

        return decrypted_file

if __name__ == "__main__":
    my_key = Path("/etc/backuper/master.key")
    my_file = Path("/home/silence-suzuka/backup_test/playground_20260807_140704.tar.gz")
    my_enc = my_file.with_suffix(my_file.suffix + ".enc")
    enc = Encryption(my_key)

    # enc.encrypt_file(my_file)
    enc.decrypt_file(my_enc)
