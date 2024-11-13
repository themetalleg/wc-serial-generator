import os
import random
import base64
import hashlib
from Crypto.Cipher import AES
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Encryption:
    """
    Encryption class provides methods to encrypt and decrypt strings using AES-256-CBC encryption
    with a fixed initialization vector and an environment-specified encryption key.
    """

    key: str = os.getenv("ENCRYPTION_KEY")
    METHOD: str = "AES-256-CBC"
    ALGORITHM: str = "sha256"
    MAXKEYSIZE: int = 32
    MAXIVSIZE: int = 16
    NUMBEROFITERATION: int = 1
    INITVECTOR: bytes = os.getenv("INIT_VECTOR", "").encode()

    @classmethod
    def maybe_encrypt(cls, key: str) -> str:
        """
        Encrypts the given key if it is not already encrypted.

        Args:
            key (str): The plaintext key to encrypt.

        Returns:
            str: The encrypted key if it was not already encrypted; otherwise, the original key.
        """
        return cls.encrypt(key) if not cls.is_encrypted(key) else key

    @classmethod
    def maybe_decrypt(cls, key: str) -> str:
        """
        Decrypts the given key if it is encrypted.

        Args:
            key (str): The encrypted key to decrypt.

        Returns:
            str: The decrypted key if it was encrypted; otherwise, the original key.
        """
        return cls.decrypt(key) if cls.is_encrypted(key) else key

    @classmethod
    def is_encrypted(cls, key: str) -> bool:
        """
        Checks if the given key is encrypted.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key is encrypted, False otherwise.
        """
        try:
            base64.b64decode(key)
            return cls.decrypt(key) is not None
        except (ValueError, TypeError):
            return False

    @classmethod
    def encrypt(cls, plain_text: str) -> str:
        """
        Encrypts plaintext using AES-256-CBC encryption.

        Args:
            plain_text (str): The plaintext to encrypt.

        Returns:
            str: The encrypted text as a base64-encoded string.
        """
        if cls.is_encrypted(plain_text):
            return plain_text
        return cls.encrypt_or_decrypt("encrypt", plain_text, cls.key)

    @classmethod
    def decrypt(cls, encrypted_text: str) -> str:
        """
        Decrypts AES-256-CBC encrypted text.

        Args:
            encrypted_text (str): The base64-encoded encrypted text to decrypt.

        Returns:
            str: The decrypted plaintext.
        """
        return cls.encrypt_or_decrypt("decrypt", encrypted_text, cls.key)

    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """
        Generates a random alphanumeric string of the specified length.

        Args:
            length (int): The length of the generated string.

        Returns:
            str: A random alphanumeric string.
        """
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return "".join(random.choices(chars, k=length))

    @classmethod
    def get_computed_hash(cls, key: str) -> str:
        """
        Computes a hashed key using SHA-256, repeated a set number of times.

        Args:
            key (str): The key to hash.

        Returns:
            str: The computed hash.
        """
        hash_val = key
        for _ in range(cls.NUMBEROFITERATION):
            hash_val = hashlib.new(cls.ALGORITHM, hash_val.encode()).hexdigest()
        return hash_val

    @classmethod
    def encrypt_or_decrypt(cls, mode: str, text: str, encryption_key: str) -> str:
        """
        Encrypts or decrypts text based on the mode specified.

        Args:
            mode (str): Either 'encrypt' or 'decrypt'.
            text (str): The plaintext or encrypted text.
            encryption_key (str): The encryption key.

        Returns:
            str: Encrypted or decrypted text based on the specified mode.
        """
        password = cls.get_computed_hash(encryption_key)[: cls.MAXKEYSIZE].encode()
        iv = cls.INITVECTOR
        cipher = AES.new(password, AES.MODE_CBC, iv)

        if mode == "encrypt":
            # Add padding to plaintext
            pad_length = cls.MAXIVSIZE - (len(text) % cls.MAXIVSIZE)
            padded_text = text + (chr(pad_length) * pad_length)
            encrypted_text = cipher.encrypt(padded_text.encode())
            return base64.b64encode(encrypted_text).decode("utf-8")
        
        # Decrypt and remove padding
        encrypted_bytes = base64.b64decode(text)
        decrypted_text = cipher.decrypt(encrypted_bytes).decode("utf-8")
        pad_length = ord(decrypted_text[-1])
        return decrypted_text[:-pad_length] if pad_length < cls.MAXIVSIZE else decrypted_text


if __name__ == "__main__":
    # Example usage
    text_to_encrypt = "1234"
    encrypted_text = Encryption.encrypt(text_to_encrypt)
    print("Encrypted:", encrypted_text)

    decrypted_text = Encryption.decrypt(encrypted_text)
    print("Decrypted:", decrypted_text)
