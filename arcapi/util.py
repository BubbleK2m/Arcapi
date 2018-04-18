import re


def strip_wiki_comment(src):
    """
    Strip wiki comment like [1], [편집]
    to get clean text

    Args:
        src: String to strip

    Return:
        Text that escaped wiki comment
    """

    return re.sub(r"(\[.+\])", '', src)


def pick_address_string(src):
    """
    Pick address string from input string with regex

    Args:
        src (str) : Text would you like get address

    Return:
        str: Address what you picked
    """

    match = re.match(r'.*?[로(지하)?|길동리]\s?(\d+-*)+\s?((번*길)\s?(\d+-*)+)?', src)
    return match.group() if match else None
