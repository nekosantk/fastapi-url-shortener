import secrets
import string
from . import crud
from sqlalchemy.orm import Session


def create_random_key(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def create_unique_key(db: Session) -> str:
    key = create_random_key()

    while crud.get_db_url_by_key(db, key):
        key = create_random_key()

    return key
