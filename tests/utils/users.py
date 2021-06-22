from api_types import User


def make_user(username: str, name: str) -> User:
    return {"username": username, "name": name, "avatar": ""}
