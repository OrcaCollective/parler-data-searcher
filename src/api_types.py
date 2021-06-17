from typing import Optional, TypedDict


class User(TypedDict):
    name: str
    username: str
    avatar: str


class PostMedia(TypedDict):
    link: str
    title: str
    image: str
    excerpt: str


class PostComment(TypedDict):
    username: str
    date: str
    text: str
    replies: int
    echos: int
    upvotes: int


class Echo(TypedDict):
    username: str
    date: str
    text: str
    impressions: int
    image: Optional[str]
    video: Optional[str]
    media: Optional[PostMedia]
    # Echos do have an echo property but it is always null
    echo: None
    comments: list[PostComment]
    comment_count: int
    echo_count: int
    upvote_count: int


class Post(TypedDict):
    username: str
    date: str
    text: str
    impressions: int
    image: Optional[str]
    video: Optional[str]
    media: Optional[PostMedia]
    echo: Optional[Echo]
    comments: list[PostComment]
    comment_count: int
    echo_count: int
    upvote_count: int
