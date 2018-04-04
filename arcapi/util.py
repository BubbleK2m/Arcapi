import re


def strip_wiki_comment(src):
    """
    strip wiki comment like [1], [편집]
    to get clean text
    :param src: String to strip
    :return:
    """
    return re.sub(r"(\[.+\])", '', src)