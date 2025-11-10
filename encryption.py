"""
NexusDEX AI - Encryption Module
================================
Криптиране и декриптиране на sensitive данни
Използва Fernet (symmetric encryption) от cryptography library
"""

import os
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from typing import Optional

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Управление на криптиране/декриптиране на данни
    Използва secret key от environment variables
    """
    
    def __init__(self):
        """Initialize encryption with secret key"""
        self.secret_key = self._get_or_create_secret_key()
        self.cipher = Fernet(self.secret_key)
    
    def _get_or_create_secret_key(self) -> bytes:
        """
        Извлича или създава encryption key
        Key се съхранява в ENV variable или генерира нов
        """
        # Опитай се да вземеш от environment
        env_key = os.environ.get('ENCRYPTION_SECRET_KEY')
        
        if env_key:
            # Валидирай и конвертирай от base64
            try:
                key = base64.urlsafe_b64decode(env_key)
                # Verify it's valid Fernet key (32 bytes)
                if len(key) == 32:
                    return base64.urlsafe_b64encode(key)
                else:
                    logger.warning("Invalid key length, generating new key")
            except Exception as e:
                logger.warning(f"Invalid encryption key format: {e}")
        
        # Генерирай нов key ако няма валиден
        new_key = Fernet.generate_key()
        
        # WARNING: В production трябва да запазиш този key!
        logger.warning(
            "⚠️ NEW ENCRYPTION KEY GENERATED! "
            "Add this to your .env file:\n"
            f"ENCRYPTION_SECRET_KEY={new_key.decode()}"
        )
        
        return new_key
    
    def encrypt(self, data: str) -> str:
        """
        Криптира string данни
        
        Args:
            data: Plain text string за криптиране
        
        Returns:
            Encrypted base64 string
        
        Example:
            encrypted = encryption.encrypt("my_api_key_123")
        """
        try:
            # Convert string to bytes
            data_bytes = data.encode('utf-8')
            
            # Encrypt
            encrypted_bytes = self.cipher.encrypt(data_bytes)
            
            # Convert to base64 string за database storage
            encrypted_string = base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
            
            return encrypted_string
            
        except Exception as e:
            logger.error(f"❌ Encryption failed: {str(e)}")
            raise
    
    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """
        Декриптира данни
        
        Args:
            encrypted_data: Encrypted base64 string
        
        Returns:
            Decrypted plain text string or None if failed
        
        Example:
            decrypted = encryption.decrypt(encrypted_api_key)
        """
        try:
            # Convert from base64 string to bytes
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            
            # Decrypt
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            
            # Convert bytes to string
            decrypted_string = decrypted_bytes.decode('utf-8')
            
            return decrypted_string
            
        except Exception as e:
            logger.error(f"❌ Decryption failed: {str(e)}")
            return None
    
    def encrypt_dict(self, data_dict: dict) -> dict:
        """
        Криптира всички values в dictionary
        
        Args:
            data_dict: Dictionary with sensitive data
        
        Returns:
            Dictionary with encrypted values
        
        Example:
            encrypted_creds = encryption.encrypt_dict({
                'api_key': 'abc123',
                'api_secret': 'xyz789'
            })
        """
        encrypted_dict = {}
        
        for key, value in data_dict.items():
            if value and isinstance(value, str):
                encrypted_dict[key] = self.encrypt(value)
            else:
                encrypted_dict[key] = value
        
        return encrypted_dict
    
    def decrypt_dict(self, encrypted_dict: dict) -> dict:
        """
        Декриптира всички values в dictionary
        
        Args:
            encrypted_dict: Dictionary with encrypted values
        
        Returns:
            Dictionary with decrypted values
        
        Example:
            creds = encryption.decrypt_dict(encrypted_creds)
        """
        decrypted_dict = {}
        
        for key, value in encrypted_dict.items():
            if value and isinstance(value, str):
                decrypted = self.decrypt(value)
                decrypted_dict[key] = decrypted if decrypted else value
            else:
                decrypted_dict[key] = value
        
        return decrypted_dict
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """
        Хешира password с PBKDF2
        По-сигурно от обикновен hash за passwords
        
        Args:
            password: Plain text password
            salt: Optional salt (генерира нов ако липсва)
        
        Returns:
            (hashed_password, salt) tuple
        
        Example:
            hashed, salt = encryption.hash_password("user_password_123")
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        
        key = kdf.derive(password.encode('utf-8'))
        hashed = base64.urlsafe_b64encode(key).decode('utf-8')
        salt_b64 = base64.urlsafe_b64encode(salt).decode('utf-8')
        
        return hashed, salt_b64
    
    def verify_password(self, password: str, hashed: str, salt_b64: str) -> bool:
        """
        Проверява дали password match-ва hash
        
        Args:
            password: Plain text password за проверка
            hashed: Stored hashed password
            salt_b64: Base64 encoded salt
        
        Returns:
            True ако password е верен, False otherwise
        
        Example:
            is_valid = encryption.verify_password(
                entered_password,
                stored_hash,
                stored_salt
            )
        """
        try:
            salt = base64.urlsafe_b64decode(salt_b64.encode('utf-8'))
            new_hash, _ = self.hash_password(password, salt)
            return new_hash == hashed
        except Exception as e:
            logger.error(f"❌ Password verification failed: {str(e)}")
            return False


# Global encryption instance
encryption_manager = EncryptionManager()


# Helper functions
def encrypt_data(data: str) -> str:
    """
    Quick encrypt function
    
    Usage:
        encrypted = encrypt_data("sensitive_info")
    """
    return encryption_manager.encrypt(data)


def decrypt_data(encrypted: str) -> Optional[str]:
    """
    Quick decrypt function
    
    Usage:
        decrypted = decrypt_data(encrypted_info)
    """
    return encryption_manager.decrypt(encrypted)


def secure_api_credentials(api_key: str, api_secret: str) -> dict:
    """
    Криптира API credentials
    
    Usage:
        encrypted_creds = secure_api_credentials(
            "my_api_key",
            "my_api_secret"
        )
    """
    return encryption_manager.encrypt_dict({
        'api_key': api_key,
        'api_secret': api_secret
    })


def retrieve_api_credentials(encrypted_creds: dict) -> dict:
    """
    Декриптира API credentials
    
    Usage:
        creds = retrieve_api_credentials(encrypted_creds)
        api_key = creds['api_key']
        api_secret = creds['api_secret']
    """
    return encryption_manager.decrypt_dict(encrypted_creds)


def hash_user_password(password: str) -> tuple:
    """
    Hash user password за database storage
    
    Usage:
        hashed_pw, salt = hash_user_password("user_password")
    """
    return encryption_manager.hash_password(password)


def verify_user_password(password: str, hashed: str, salt: str) -> bool:
    """
    Verify user password при login
    
    Usage:
        is_valid = verify_user_password(
            entered_password,
            stored_hash,
            stored_salt
        )
    """
    return encryption_manager.verify_password(password, hashed, salt)
