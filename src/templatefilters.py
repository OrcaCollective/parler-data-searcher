import re
from re import Match
from typing import Any, Optional

from quart import Quart, url_for

from constants import (
    INCLUDE_MENTIONS_QUERY_PARAM,
    POSTS_PATH_COMPONENT,
    SEARCH_CONTENT_QUERY_PARAM,
    USERNAME_QUERY_PARAM,
)


SEARCH_LINK_TEMPLATE = '<a href="{url}">{text}</a>'
HIGHLIGHT_SEARCHED_TERM_TEMPLATE = "<mark>\\1</mark>"

USERNAME_AND_HASHTAG_REGEX = re.compile(r"[@|#]\w+")


def _create_search_link(m: Match):
    matched_word = m.group(0)

    if matched_word.startswith("@"):
        params = {
            USERNAME_QUERY_PARAM: matched_word,
            INCLUDE_MENTIONS_QUERY_PARAM: "true",
        }
    else:
        params = {SEARCH_CONTENT_QUERY_PARAM: matched_word}

    # create hashtag link
    return SEARCH_LINK_TEMPLATE.format(
        url=url_for(POSTS_PATH_COMPONENT, **params),
        text=matched_word,
    )


def with_search_links(s: str):
    """
    Look for hashtags and usernames. If found, inject a link that will search for that term.

    :param s: string to template links into
    :return: string with usernames and hashtag links templated into it
    """
    if not s:
        return s

    with_links = USERNAME_AND_HASHTAG_REGEX.sub(_create_search_link, s)

    return with_links


def with_highlighted_term(s: str, highlighter_regex: Optional[re.Pattern[Any]]):
    if not s or highlighter_regex is None:
        return s

    with_highlighted_terms = re.sub(
        highlighter_regex, HIGHLIGHT_SEARCHED_TERM_TEMPLATE, s
    )

    return with_highlighted_terms


def register_filters(app: Quart):
    """
    Register all filters with the main app.

    :param app:
    :return:
    """
    app.add_template_filter(with_search_links)
    app.add_template_filter(with_highlighted_term)
