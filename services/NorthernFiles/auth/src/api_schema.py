from Crypto.PublicKey import RSA
import base64

from apiflask import Schema
from apiflask.fields import Integer, String, List, Nested
from apiflask.validators import Length
from marshmallow import ValidationError


class Base64Bytes(String):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ''
        return base64.b64encode(value).decode()

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            assert base64.b64encode(base64.b64decode(
                value.encode())).decode() == value
            return base64.b64decode(value.encode())
        except:
            raise ValidationError("Invalid proof, expected base64 data")


class UserPostRequest(Schema):
    username = String(required=True, validate=Length(5))
    name = String(required=True, validate=Length(3))
    capsule = Base64Bytes(required=True)


class UserResponse(Schema):
    id = String(required=True)
    username = String(required=True)
    capsule = Base64Bytes(required=True)


class ChallengeRequest(Schema):
    user_id = String(required=True)
    X_u = String(required=True)
    alpha = String(required=True)


class ChallengeResponse(Schema):
    ss_id = String(required=True)
    beta = String(required=True)
    C = String(required=True)
    X_s = String(required=True)


class LoginRequest(Schema):
    ss_id = String(required=True)
    A_u = String(required=True)


class TokenResponse(Schema):
    token = String(required=True)
    expiration = Integer(required=True)


class JWK(Schema):
    e = String(required=True)
    kid = String(required=True)
    kty = String(required=True)
    n = String(required=True)


class KeysResponse(Schema):
    keys = List(Nested(JWK), required=True)
