from flask import jsonify, request
import requests

from src.logger import logger
from src.controllers.token_controller import create_token, check_sign, check_jti


def proxy_request():
    values = request.get_json()
    logger.debug(values)
    data = values.get('payload')
    logger.debug(data)
    sign = request.headers.get('X-SIGNATURE')
    logger.debug(sign)
    
    sub = data.get('sub')
    logger.debug(sub)
    res = check_sign(sub, sign, request.json['payload'])
    logger.debug(res)
    if res['status'] != 'OK':
        return jsonify({'status': res['status']}), 400
    
    jti = data.get('jti')
    logger.debug(jti)
    if check_jti(jti) == 'BAD':
        jsonify({'status': 'BAD jti'}), 400
    
    path = data.get('path')
    logger.debug(path)
    request_data = data.get('data')
    logger.debug(path)
    r = requests.post(
        path,
        json={'payload': request_data},
        timeout=10
    )
    logger.debug(path)
    return r.json()
    

def init_session():
    values = request.get_json()
    data = values.get('payload')
    sub = data.get('sub')
    sign = request.headers.get('X-SIGNATURE')
    
    
    res = check_sign(sub, sign, request.json['payload'])
    jti = data.get('jti')
    
    if res['status'] == 'OK':
        jti = create_token(sub, jti)
        return jsonify({'status': 'OK', 'jti' : jti})
    return jsonify({'status': res['status']}), 400
    
    