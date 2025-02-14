import os

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


with open(os.path.join(os.path.dirname(__file__), "../../keys/private_key.pem"), "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
    )


with open(os.path.join(os.path.dirname(__file__), "../../keys/public_key.pem"), "rb") as key_file:
    public_key = serialization.load_pem_public_key(key_file.read())


def encrypt_data(data_to_encrypt: str) -> bytes:
    if not isinstance(data_to_encrypt, str):
        data_to_encrypt = str(data_to_encrypt)

    data = bytes(data_to_encrypt, encoding="utf-8")

    encrypted_data = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted_data


def decrypt_data(encrypted_data: bytes) -> bytes:
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return decrypted_data


def get_masked_payment(encrypted_data: memoryview) -> str:
    decrypted_data = decrypt_data(encrypted_data.tobytes()).decode("utf-8")
    masked_payment = "****" * 3 + decrypted_data[-4:]

    return masked_payment
