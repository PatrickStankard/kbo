# -*- coding: utf-8 -*-

import datetime
import re
import urllib.parse

KST_TZINFO = datetime.timezone(
    offset=datetime.timedelta(hours=9),
    name='Asia/Seoul'
)

KBO_LEAGUE_TEAM_NAME_SHORT_TO_LONG = {
    '두산': 'Doosan Bears',
    '한화': 'Hanwha Eagles',
    'KIA': 'Kia Tigers',
    '키움': 'Kiwoom Heroes',
    'KT': 'KT Wiz',
    'LG': 'LG Twins',
    '롯데': 'Lotte Giants',
    'NC': 'NC Dinos',
    '삼성': 'Samsung Lions',
    'SK': 'SK Wyverns'
}

KBO_LEAGUE_TEAM_NAMES_SHORT = KBO_LEAGUE_TEAM_NAME_SHORT_TO_LONG.keys()
KBO_LEAGUE_TEAM_NAMES_LONG = KBO_LEAGUE_TEAM_NAME_SHORT_TO_LONG.values()

KBO_LEAGUE_TEAM_NAME_UNKNOWN = 'Unknown Team'

NAVER_TV_CHANNEL_PATH_TO_KBO_LEAGUE_TEAM_NAME_LONG = {
    '/bearsvod': 'Doosan Bears',
    '/eaglesvod': 'Hanwha Eagles',
    '/tigersvod': 'Kia Tigers',
    '/heroesvod': 'Kiwoom Heroes',
    '/ktwizvod': 'KT Wiz',
    '/twinsvod': 'LG Twins',
    '/giantsvod': 'Lotte Giants',
    '/ncdinosvod': 'NC Dinos',
    '/lionsvod': 'Samsung Lions',
    '/wyvernsvod': 'SK Wyverns',
    '/kbaseball': 'KBO League'
}

NAVER_TV_CHANNEL_PATHS = NAVER_TV_CHANNEL_PATH_TO_KBO_LEAGUE_TEAM_NAME_LONG.keys()

NAVER_TV_CLIP_TYPE_FULL_GAME = 'full_game'
NAVER_TV_CLIP_TYPE_CONDENSED_GAME = 'condensed_game'
NAVER_TV_CLIP_TYPE_UNKNOWN = 'unknown'

NAVER_TV_CLIP_FULL_GAME_TITLE_REGEX = re.compile(
    r"^(?P<away_team_name>[^\-\s]+)-(?P<home_team_name>[^\-\s]+) 풀영상$"
)
NAVER_TV_CLIP_CONDENSED_GAME_TITLE_REGEX = re.compile(
    r"^\[?전체HL\]? -?(?P<description>.+)$"
)

NAVER_TV_SCHEME = 'https'
NAVER_TV_NETLOC = 'tv.naver.com'
NAVER_TV_SEARCH_CLIP_PATH = '/search/clip'

NAVER_TV_SEARCH_CLIP_FULL_GAME_QUERY = {
    'query': '"풀영상" "KBO리그"',
    'sort': 'date',
    'isTag': 'false'
}
NAVER_TV_SPIDER_FULL_GAME_URL = urllib.parse.urlunparse((
    NAVER_TV_SCHEME,
    NAVER_TV_NETLOC,
    NAVER_TV_SEARCH_CLIP_PATH,
    '',
    urllib.parse.urlencode(
        NAVER_TV_SEARCH_CLIP_FULL_GAME_QUERY,
        quote_via=urllib.parse.quote
    ),
    '',
))

NAVER_TV_SEARCH_CLIP_CONDENSED_GAME_QUERY = {
    'query': '"[전체HL]" "KBO리그"',
    'sort': 'date',
    'isTag': 'false'
}
NAVER_TV_SPIDER_CONDENSED_GAME_URL = urllib.parse.urlunparse((
    NAVER_TV_SCHEME,
    NAVER_TV_NETLOC,
    NAVER_TV_SEARCH_CLIP_PATH,
    '',
    urllib.parse.urlencode(
        NAVER_TV_SEARCH_CLIP_CONDENSED_GAME_QUERY,
        quote_via=urllib.parse.quote
    ),
    '',
))

GAME_CLIP_SHOW_NAME = 'KBO League'
GAME_CLIP_THUMBNAIL_TIMESTAMP = '00:00:03'
GAME_CLIP_DATE_RELEASED_TEMPLATE = "{year}-{month:02d}-{day:02d}"

FULL_GAME_CLIP_TITLE_TEMPLATE = "{away_team_name} at {home_team_name}"
FULL_GAME_CLIP_FILENAME_TEMPLATE = "KBO League - S{year}E{clip_id} - {year}.{month:02d}.{day:02d} - {away_team_name} at {home_team_name}.mp4"
FULL_GAME_CLIP_THUMBNAIL_FILENAME_TEMPLATE = "KBO League - S{year}E{clip_id} - {year}.{month:02d}.{day:02d} - {away_team_name} at {home_team_name}.jpg"

CONDENSED_GAME_CLIP_TITLE_TEMPLATE = "{away_team_name} at {home_team_name} (condensed)"
CONDENSED_GAME_CLIP_FILENAME_TEMPLATE = "KBO League - S{year}E{clip_id} - {year}.{month:02d}.{day:02d} - {away_team_name} at {home_team_name} (condensed).mp4"
CONDENSED_GAME_CLIP_THUMBNAIL_FILENAME_TEMPLATE = "KBO League - S{year}E{clip_id} - {year}.{month:02d}.{day:02d} - {away_team_name} at {home_team_name} (condensed).jpg"

MUTAGEN_TAG_ARTIST_KEY = '\xa9ART'
MUTAGEN_TAG_TV_SHOW_KEY = 'tvsh'
MUTAGEN_TAG_TITLE_KEY = '\xa9nam'
MUTAGEN_TAG_DATE_RELEASED_KEY = '\xa9day'
