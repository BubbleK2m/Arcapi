from arcapi.util import strip_wiki_comment, pick_address_string
from bs4 import BeautifulSoup as Soup

import requests
import re

GAME_CENTER_WIKI_URL = 'https://namu.wiki/w/오락실/{}'

CITIES = [
    '서울', '인천',
    '경기/남부', '경기/북부', '강원',
    '대전', '세종', '충남', '충북',
    '부산', '울산', '경남', '경북',
    '광주', '전남', '전북',
    '제주',
]


def get_game_center_url(city):
    return GAME_CENTER_WIKI_URL.format(city)


def get_partition_from_rows(rows):
    pivot = -1

    for i, row in enumerate(rows):
        if re.findall(r'가동 중인 기기|가격|수량', row.get_text().strip()):
            pivot = i
            break

    return (rows[:pivot], rows[pivot:]) if pivot != -1 else None


def get_game_center_from_rows(rows):
    name, kind = rows[0].select('td')[:2]
    items = {}

    for row in rows[2:]:
        chunks = row.select('td')[:2]

        if len(chunks) == 2:
            key, item = row.select('td')[:2]
            items[key.get_text().strip()] = item

    address = items.get('주소')
    opening = items.get('영업시간')

    return {
        'name': strip_wiki_comment(name.get_text().strip()),
        'kind': strip_wiki_comment(kind.get_text().strip()),
        'opening': strip_wiki_comment(opening.get_text().strip()) if opening else None,
        'address': pick_address_string(strip_wiki_comment(address.get_text().strip())) if address else None,
    }


def get_games_from_rows(rows):
    games = []
    headers = [i.get_text().strip() for i in rows[0].select('td')]

    for row in rows[1:]:
        if re.findall(r'\d+원|\d+[조대]', row.get_text().strip()):
            chunks = row.select('td')
            items = {}

            for i, header in enumerate(headers):
                if i < len(chunks):
                    items[header] = chunks[i]

            name = items['가동 중인 기기']
            price = items.get('가격')
            count = items.get('수량')

            games.append({
                'name': strip_wiki_comment(name.get_text().strip()),
                'price': strip_wiki_comment(price.get_text().strip()) if price else None,
                'count': strip_wiki_comment(count.get_text().strip()) if count else None,
            })

    return games


def get_game_centers_from_soup(soup):
    centers = []

    for content in [h.next_sibling for h in soup.select('.wiki-heading') if re.findall(r'[ⓚⓝⓢⓣ]+', h.text)]:
        if len(re.findall(r"주소|영업시간|가동 중인 기기|수량|가격", content.text)) >= 5:
            wiki_lists = content.select('.wiki-list')
            wiki_table_rows = content.select('.wiki-table tr')

            if not wiki_lists and wiki_table_rows:
                center_rows, game_rows = get_partition_from_rows(wiki_table_rows)
                center = get_game_center_from_rows(center_rows)

                center['game'] = get_games_from_rows(game_rows)
                centers.append(center)

    return centers


def get_game_centers_from_city(city):
    resp = requests.get(get_game_center_url(city))
    soup = Soup(resp.text, 'html.parser')

    return get_game_centers_from_soup(soup)
