import re
from re import Match

from jinja2 import Markup
from quart import url_for, Quart

from constants import (
    USERNAME_QUERY_PARAM,
    SEARCH_CONTENT_QUERY_PARAM,
    POSTS_PATH_COMPONENT,
)

SEARCH_LINK_TEMPLATE = '<a href="{url}">{text}</a>'

USERNAME_REGEX = re.compile(r"@\w+")
HASHTAG_REGEX = re.compile(r"#\w+")


def with_search_links(s: str):
    """
    Look for hashtags and usernames. If found, inject a link that will search for that term.

    :param s: string to template links into
    :return: string with usernames and hashtag links templated into it
    """
    if not s:
        return s

    with_user_links = USERNAME_REGEX.sub(_create_user_search_link, s)
    with_hashtag_links = HASHTAG_REGEX.sub(_create_hashtag_search_link, with_user_links)

    return Markup(with_hashtag_links)


def _create_user_search_link(m: Match):
    return SEARCH_LINK_TEMPLATE.format(
        url=url_for(POSTS_PATH_COMPONENT, **{USERNAME_QUERY_PARAM: m.group(0)}),
        text=m.group(0),
    )


def _create_hashtag_search_link(m: Match):
    return SEARCH_LINK_TEMPLATE.format(
        url=url_for(POSTS_PATH_COMPONENT, **{SEARCH_CONTENT_QUERY_PARAM: m.group(0)}),
        text=m.group(0),
    )


def register_filters(app: Quart):
    """
    Register all filters with the main app.

    :param app:
    :return:
    """
    app.add_template_filter(with_search_links)
