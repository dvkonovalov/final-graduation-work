import json
import requests

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding

from src.logger import logger


def init_session():
        
    request_data = {
        "sub" : "data_collector",
    }
    
    signature = sign(request_data)
    
    logger.debug(signature.hex())
    
    r = requests.post(
        'http://gateway:5010/init_session',
        json={'payload': request_data},
        headers={'X-SIGNATURE': signature.hex()},
        timeout=10
    )
    
    return r.json().get('jti')

def proxy(jti : str, path : str, data : dict, method=None):
    request_data = {
        'jti' : jti,
        'data' : data,
        'path' : path,
        'sub' : 'data_collector'
    }
    logger.debug(request_data)
    signature = sign(request_data)
    
    
    r = requests.post(
        'http://gateway:5010/proxy',
        json={'payload': request_data},
        headers={'X-SIGNATURE': signature.hex()},
        timeout=10
    )
    
    return r.json()

def sign(request_data):
    with open('private_key.pem', 'rb') as priv_file:
        private_key_loaded = load_pem_private_key(
            priv_file.read(),
            password=b'dba21ddc-665d-40e5-8f54-8fbae6c40192',
            backend=default_backend()
        )
        
    data_string = json.dumps(request_data, sort_keys=True)
    
    signature = private_key_loaded.sign(
        data=data_string.encode(),
        padding=padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        algorithm=hashes.SHA256()
    )
    return signature
    