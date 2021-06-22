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
        "date": "",
        "impressions": 0,
        "image": None,
        "video": None,
        "comment_count": len(comments),
        "echo_count": 0,
        "upvote_count": 0,
    }
