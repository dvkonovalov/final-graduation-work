from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend
from datetime import datetime
import json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.padding import PSS, MGF1
from cryptography.exceptions import InvalidSignature

from src.logger import logger
from src.models.token import Token
from src.db import db

def read_public_sert(filepath : str):
    with open(f'public_serts/{filepath}', 'rb') as pub_file:
        public_key_loaded = load_pem_public_key(
            pub_file.read(),
            backend=default_backend()
        )
    return public_key_loaded

CONFIG = {
    'data_collector': read_public_sert('data_collector.pem'),
    'preparing_module': read_public_sert('preparing_module.pem'),
}

def create_token(sub:str, jti : str):
    Token.query.filter(Token.iat < datetime.utcnow()).delete()
    
    if jti:
        token = Token.query.filter(Token.jti == jti).first()
        if token:
            return jti
    
    new_token = Token(sub = sub)
    db.session.add(new_token)
    db.session.commit()
    return new_token.jti

def check_jti(jti : str):
    token = Token.query.filter(Token.jti == jti).first()
    if token and token.jti == jti:
        return 'OK'
    return 'BAD'

def check_sign(sub : str, sign, payload):
    if sub in CONFIG:
        try:
            signature = bytes.fromhex(sign)
        except ValueError:
            return {'status': 'Invalid hexadecimal signature'}
        serialized_payload = json.dumps(payload, sort_keys=True).encode()
        try:
            CONFIG[sub].verify(
                signature,
                serialized_payload,
                PSS(mgf=MGF1(hashes.SHA256()), salt_length=PSS.MAX_LENGTH),
                hashes.SHA256()
            )
        except InvalidSignature:
            return {'status': 'Invalid signature'}
        return {'status': 'OK'}
    return {'status': 'Invalid sub'}