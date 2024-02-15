import logging

import jwt


class JWTHelper(object):
    ALGORITHM = "HS256"

    def __init__(self, security_key):
        self.security_key = security_key

    def gen_token(self, data):
        try:
            return jwt.encode(data, self.security_key, algorithm=self.ALGORITHM)
        except Exception as e:
            logging.error("failed to generate jwt token: {}".format(e))
            return ""

    def decode_token(self, cookie):
        try:
            return jwt.decode(cookie, self.security_key, algorithms=[self.ALGORITHM, ])
        except Exception as e:
            logging.error("failed to decode jwt token: {}".format(e))
            return None
