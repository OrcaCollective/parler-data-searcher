import re
from re import Match
from typing import Any, Optional

from jinja2 import Markup
from quart import url_for, Quart

from constants import (
    USERNAME_QUERY_PARAM,
    SEARCH_CONTENT_QUERY_PARAM,
    POSTS_PATH_COMPONENT,
)

SEARCH_LINK_TEMPLATE = '<a href="{url}">{text}</a>'
HIGHLIGHT_SEARCHED_TERM_TEMPLATE = "<mark>\\1</mark>"

USERNAME_AND_HASHTAG_REGEX = re.compile(r"[@|#]\w+")


def with_search_links(s: str):
    """
    Look for hashtags and usernames. If found, inject a link that will search for that term.

    :param s: string to template links into
    :return: string with usernames and hashtag links templated into it
    """
    if not s:
        return s

    with_links = USERNAME_AND_HASHTAG_REGEX.sub(_create_search_link, s)

    return Markup(with_links)


def _create_search_link(m: Match):
    if m.group(0).startswith("@"):
        # create username link
        return SEARCH_LINK_TEMPLATE.format(
            url=url_for(POSTS_PATH_COMPONENT, **{USERNAME_QUERY_PARAM: m.group(0)}),
            text=m.group(0),
        )
    else:
        # create hashtag link
        return SEARCH_LINK_TEMPLATE.format(
            url=url_for(
                POSTS_PATH_COMPONENT, **{SEARCH_CONTENT_QUERY_PARAM: m.group(0)}
            ),
            text=m.group(0),
        )


def with_highlighted_term(s: str, content_regex: Optional[re.Pattern[Any]]):
    if not s or content_regex is None:
        return s

    with_highlighted_terms = re.sub(content_regex, HIGHLIGHT_SEARCHED_TERM_TEMPLATE, s)

    return Markup(with_highlighted_terms)


def register_filters(app: Quart):
    """
    Register all filters with the main app.

    :param app:
    :return:
    """
    app.add_template_filter(with_search_links)
    app.add_template_filter(with_highlighted_term)
