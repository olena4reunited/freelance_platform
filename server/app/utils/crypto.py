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


def encrypt_data(data_to_encrypt: bytes) -> bytes:
    encrypted_data = public_key.encrypt(
        data_to_encrypt,
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
