from flask import request
import json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding

from src.logger import logger

def init_session():
    with open('../private_key.pem', 'rb') as priv_file:
        private_key_loaded = load_pem_private_key(
            priv_file.read(),
            password=b'dba21ddc-665d-40e5-8f54-8fbae6c40192',
            backend=default_backend()
        )
        
    request_data = {
        "sub" : "data_collector"
    }
    
    data_string = json.dumps(request_data, sort_keys=True)
    
    signature = private_key_loaded.sign(
        data=data_string.encode(),
        padding=padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        algorithm=hashes.SHA256()
    )
    
    r = request.post(
        'http://localhost:5001/check',
        json={'payload': request_data},
        headers={'X-SIGNATURE': signature.hex()}
    )
    
    logger.info(r.json())
    