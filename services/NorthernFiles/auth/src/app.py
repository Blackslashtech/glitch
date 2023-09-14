import secrets
import os
import json
import uuid
from pathlib import Path

from apiflask import APIFlask

from db_models import User, LoginServerStorage, db
from api_schema import UserPostRequest, UserResponse, ChallengeRequest, ChallengeResponse, TokenResponse, LoginRequest, KeysResponse
from Crypto.PublicKey import RSA
from jwcrypto import jwk, jwt

app = APIFlask(__name__, docs_path=None, spec_path=None)

app.secret_key = secrets.token_hex(24)

if not os.getenv('DRY_RUN'):
    import cryptolib

    DATABASE_HOST = os.getenv('DATABASE_HOST')
    DATABASE_DB = os.getenv('DATABASE_DB')
    DATABASE_USER = os.getenv('DATABASE_USER')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_DB}'

    db.init_app(app)

    with app.app_context():
        db.create_all()


# JWT key
jwtKey = jwk.JWK.generate(kty='RSA', kid=str(uuid.uuid4()), size=4096)
Path("/tmp/keys").mkdir(parents=True, exist_ok=True)
with open(f'/tmp/keys/{os.getpid()}', 'w') as f:
    f.write(jwtKey.export(private_key=False))


@app.post('/user')
@app.input(UserPostRequest)
@app.output(UserResponse)
def create_user(body: dict):
    user = User(name=body['name'], username=body['username'], capsule=body['capsule'])

    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        return '', 409
    db.session.refresh(user)

    return user.serialize


@app.get("/user/<string:username>")
@app.output(UserResponse)
def get_user_by_username(username: str):
    user = db.first_or_404(db.select(User).filter_by(username=username))
    return user.serialize


@app.post("/user/<string:username>/challenge")
@app.input(ChallengeRequest)
@app.output(ChallengeResponse)
def get_user_challenge(username: str, body: dict):
    user = db.first_or_404(db.select(User).filter_by(username=username))

    cs1 = cryptolib.ClientStep1()
    cs1.user_id = body['user_id']
    cs1.X_u = body['X_u']
    cs1.alpha = body['alpha']

    capsule = cryptolib.Capsule()
    db_capsule = json.loads(user.capsule)
    capsule.success = db_capsule['success']
    capsule.user_id = db_capsule['user_id']
    capsule.ks = db_capsule['ks']
    capsule.ps = db_capsule['ps']
    capsule.Ps = db_capsule['Ps']
    capsule.Pu = db_capsule['Pu']
    capsule.C = db_capsule['C']
    capsule.sk = db_capsule['sk']
    capsule.pk = db_capsule['pk']

    [ss1, ss] = cryptolib.server_step1(cs1, capsule)

    db_ss = LoginServerStorage(user_id=user.id, ss=json.dumps({
        'K_sess': ss.K_sess,
        'id1': ss.id1,
    }).encode())
    db.session.add(db_ss)
    db.session.commit()
    db.session.refresh(db_ss)

    return {
        'ss_id': db_ss.id,
        'beta': ss1.beta,
        'C': ss1.C,
        'X_s': ss1.X_s,
    }


@app.post("/user/<string:username>/session")
@app.input(LoginRequest)
@app.output(TokenResponse)
def login(username: str, body: dict):
    user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one()
    if not user:
        return '', 401
    
    ss_id = body['ss_id']
    db_ss = db.session.execute(db.select(LoginServerStorage).filter_by(id=ss_id,user_id=user.id)).scalar_one()
    if not db_ss:
        return '', 401

    cs2 = cryptolib.ClientStep2()
    cs2.A_u = body['A_u']

    ss = cryptolib.ServerStorage()
    decoded_ss = json.loads(db_ss.ss)
    ss.K_sess = decoded_ss['K_sess']
    ss.id1 = decoded_ss['id1']

    db.session.delete(db_ss)
    db.session.commit()

    if cryptolib.server_step2(cs2, ss):
        return generate_token(user)
    return '', 401


@app.get("/jwks")
@app.output(KeysResponse)
def get_keys():
    keys = []
    for key in os.listdir('/tmp/keys/'):
        with open(f'/tmp/keys/{key}', 'r') as f:
            keys.append(json.loads(f.read()))
    return {'keys': keys}


@app.get("/internal/token/<uuid:id>")
@app.output(TokenResponse)
@app.doc(hide=True)
def internal_generate_token(id: str):
    user = db.get_or_404(User, id)
    return generate_token(user)


def generate_token(user: User):
    token = jwt.JWT(header={'alg': 'RS256', 'kid': jwtKey.key_id}, claims=user.serialize_no_key)
    token.make_signed_token(jwtKey)
    return {'token': token.serialize(), 'expiration': 10}
