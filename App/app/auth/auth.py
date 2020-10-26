
import json
import os
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from os import environ as env


AUTH0_DOMAIN = ''#os.environ['AUTH0_DOMAIN']
ALGORITHMS = ''#os.environ['ALGORITHMS']
API_AUDIENCE = ''#os.environ['API_AUDIENCE']

# AuthError Exception
"""
AuthError Exception
A standardized way to communicate auth failure modes
"""


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

""" get_token_auth_header()
This function obtains the access token from the Authorization Header

    @INPUTS: N/A

    @RETURNS: token

    @RAISES:
    Authorization header errors

    Raises:
        AuthError: 401 - No Authorization header found
        AuthError: 401 - Authorization header must be a bearer token
        AuthError: 401 - Authorization header must start with "Bearer"

"""


def get_token_auth_header():
    if 'Authorization' not in request.headers:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'No Authorization header found.'
        }, 401)

    header = request.headers['Authorization']
    header_parts = header.split()
    if len(header_parts) != 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must ONLY be bearer token.'
        }, 401)

    if header_parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    token = header_parts[1]
    return token


"""check_permissions(permission, payload)

    checks permissions of the token making the request

    @INPUTS
    permission: string permission (i.e. 'get:movies')
    payload: decoded jwt payload

    @RETURNS: True

    @RAISES:
    Authorization errors if permissions are missing

    Raises:
        AuthError: 400 - Permission not included in JWT
        AuthError: 401 - Permission not found in JWT

"""


def check_permissions(permission, payload):
    '''This function checks the permissions that are in the
    JWT to see if the request permission is in the request'''

    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found in JWT.'
        }, 401)

    return True


""" verify_decode_jwt(token) method

    Verifies and returns decoded token payload

    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims

    @RETURNS
        payload
"""


def verify_decode_jwt(token):
    # Get the public key from Auth0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # Get the data in the header
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}

    # Raise error if missing 'kid'
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    # Verify
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'success': False,
                'message': 'Token Expired',
                'error': 401
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'success': False,
                'message': 'Incorrect claims. Please check the\
                                            audience and issuer',
                'error': 401
            }, 401)

        except jwt.JWTError:
            raise AuthError({
                'success': False,
                'message': 'Invalid authentication token signature.',
                'error': 401
            }, 401)

        except Exception:
            raise AuthError({
                'success': False,
                'message': 'Unable to parse authentication token',
                'error': 400
            }, 400)

    raise AuthError({
        'success': False,
        'message': 'unable to find the appropriate key',
        'error': 400,
    }, 400)


"""@requires_auth(permission)

    @INPUTS
        permission: string permission (i.e. 'post:actor')

    @RETURNS
        requires_auth_decorator

    -Uses the get_token_auth_header method to get the token
    -Uses the verify_decode_jwt method to decode the jwt
    -Uses the check_permissions method validate claims
     and checks the requested permission
    -Return the decorator which passes
    the decoded payload to the decorated method

"""


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
