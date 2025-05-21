from flask import request
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.backends import default_backend


def read_public_sert(filepath : str):
    with open(f'public_serts/{filepath}', 'rb') as pub_file:
        public_key_loaded = load_pem_public_key(
            pub_file.read(),
            backend=default_backend()
        )
    return public_key_loaded

def check_token():
    pass