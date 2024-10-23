from passlib.context import CryptContext

context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hash(password):
    return context.hash(password)


def verify_password(plain_password, hashed_password):
    return context.verify(plain_password, hashed_password)
