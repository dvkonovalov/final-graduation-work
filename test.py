from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import uuid

# Генерация приватного ключа RSA
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Создание публичного ключа из приватного
public_key = private_key.public_key()

# Создаем пароль для защиты приватного ключа
password = str(uuid.uuid4()).encode("utf-8")

print(password)

# Сохраняем приватный ключ в файл с паролем
with open('private_key.pem', 'wb') as priv_file:
    priv_file.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password)
    ))

# Сохраняем публичный ключ в отдельный файл
with open('preparing_module.pem', 'wb') as pub_file:
    pub_file.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))