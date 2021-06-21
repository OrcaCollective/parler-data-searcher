from typing import Optional
from api_types import Echo, Post, PostComment, PostMedia


def make_post(
    username: str,
    text: str,
    comments: list[PostComment],
    echo: Optional[Echo],
    media: Optional[PostMedia],
) -> Post:
    return {
        "username": username,
        "text": text,
        "comments": comments,
        "media": media,
        "echo": echo,
    }
