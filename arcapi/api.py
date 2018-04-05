from arcapi.util import strip_wiki_comment
from bs4 import BeautifulSoup as Soup

import requests
import re

GAME_CENTER_WIKI_URL = 'https://namu.wiki/w/오락실'

CITIES = [
    '서울', '인천',
    '경기/남부', '경기/북부', '강원',
    '대전', '세종', '충남', '충북',
    '부산', '울산', '경남', '경북',
    '광주', '전남', '전북',
    '제주'
]


def get_game_centers_from_wiki_table(wiki_tables):
    """
    Get game centers from wiki table
    about game centers

    :param wiki_tables: Wiki table
    :type wiki_tables: list

    :return: Game center dictionary list
    :rtype: list
    """

    centers = []

    # first table was saved information in game center
    if len(wiki_tables) >= 1:
        rows = wiki_tables[0].select('tr')
        center = {}

        try:
            # get information about game center
            center['name'] = strip_wiki_comment(rows[0].select('td')[0].get_text().strip()) or None
            center['kind'] = strip_wiki_comment(rows[0].select('td')[1].get_text().strip()) or None
            center['address'] = strip_wiki_comment(rows[2].select('td')[1].get_text().strip()) or None
            center['opening'] = strip_wiki_comment(rows[4].select('td')[1].get_text().strip()) or None

        except IndexError:
            pass

        center['games'] = []

        if len(wiki_tables) >= 2:
            # second table was saved information games in document
            rows = wiki_tables[1].select('tr')
            rows = [r for r in rows if len(r.select('td')) == 4]

            for row in rows[1:]:
                game = {}

                try:
                    # get information of game from game center
                    game['name'] = strip_wiki_comment(row.select('td')[0].get_text().strip()) or None
                    game['count'] = strip_wiki_comment(row.select('td')[1].get_text().strip()) or None
                    game['price'] = strip_wiki_comment(row.select('td')[2].get_text().strip()) or None
                    game['comment'] = strip_wiki_comment(row.select('td')[3].get_text().strip()) or None

                except IndexError:
                    pass

                center['games'].append(game)

        centers.append(center)

    return centers


def get_game_centers_from_city(city_name):
    """
    Get game centers from namu wiki article
    currently, only parse wiki table T0T

    :param city_name: City name what you'll get game centers
    :type city_name: str

    :return Game center dictionary list
    :rtype: list
    """

    if city_name not in CITIES:
        return None

    centers = []

    # get wiki article about game centers in city
    resp = requests.get('{0}/{1}'.format(GAME_CENTER_WIKI_URL, city_name))
    soup = Soup(resp.text, 'html.parser')

    # get game titles from game center wiki article that has ⓚ, ⓝ, ⓢ, ⓣ symbol
    # that means online games are available
    headings = soup.select('.wiki-heading')
    contents = [h.next_sibling for h in headings if re.match(r'.*[ⓚⓝⓢⓣ].*', h.get_text())]

    for content in contents:
        wiki_tables = content.select('.wiki-table')

        if len(wiki_tables) > 0:
            # if wiki table based content, we'll parse wiki table
            centers.extend(get_game_centers_from_wiki_table(wiki_tables))

    return centers
