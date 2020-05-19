# -*- coding: utf-8 -*-

import csv
import datetime
import os
import urllib

import dateparser
import scrapy

from kbo.constants import (
    KBO_LEAGUE_TEAM_NAMES_LONG,
    KBO_LEAGUE_TEAM_NAME_SHORT_TO_LONG,
    KBO_LEAGUE_TEAM_NAME_UNKNOWN,
    KST_TZINFO,
    NAVER_TV_CHANNEL_PATH_TO_KBO_LEAGUE_TEAM_NAME_LONG,
    NAVER_TV_CLIP_CONDENSED_GAME_TITLE_REGEX,
    NAVER_TV_CLIP_FULL_GAME_TITLE_REGEX,
    NAVER_TV_CLIP_TYPE_CONDENSED_GAME,
    NAVER_TV_CLIP_TYPE_FULL_GAME,
    NAVER_TV_CLIP_TYPE_UNKNOWN,
    NAVER_TV_NETLOC,
    NAVER_TV_SCHEME,
    NAVER_TV_SEARCH_CLIP_CONDENSED_GAME_QUERY,
    NAVER_TV_SEARCH_CLIP_FULL_GAME_QUERY,
    NAVER_TV_SEARCH_CLIP_PATH
)
from kbo.items import NaverTvClip


class NaverTvSpider(scrapy.Spider):

    name = 'naver_tv'
    allowed_domains = [NAVER_TV_NETLOC]

    _full_game_feed = None
    _num_pages = None

    clip_type = None
    team_name = None
    end_date = None
    start_date = None
    min_clip_length = None
    max_clip_length = None
    max_num_pages = None
    do_dry_run = None
    output_dir_path = None
    tmp_dir_path = None
    full_game_feed_path = None

    def __init__(self,
                 clip_type=None,
                 team_name=None,
                 end_date=None,
                 start_date=None,
                 min_clip_length=None,
                 max_clip_length=None,
                 max_num_pages=None,
                 output_dir_path=None,
                 tmp_dir_path=None,
                 full_game_feed_path=None,
                 do_dry_run=None,
                 *args,
                 **kwargs):
        super(NaverTvSpider, self).__init__(*args, **kwargs)

        self.clip_type = self._parse_clip_type(clip_type)
        self.team_name = self._parse_team_name(team_name)
        self.end_date = self._parse_end_date(end_date)
        self.start_date = self._parse_start_date(start_date)
        self.min_clip_length = self._parse_min_clip_length(min_clip_length)
        self.max_clip_length = self._parse_max_clip_length(max_clip_length)
        self.max_num_pages = self._parse_max_num_pages(max_num_pages)
        self.do_dry_run = self._parse_do_dry_run(do_dry_run)
        self.output_dir_path = self._parse_output_dir_path(output_dir_path)
        self.tmp_dir_path = self._parse_tmp_dir_path(tmp_dir_path)
        self.full_game_feed_path = self._parse_full_game_feed_path(full_game_feed_path)

    def start_requests(self):
        yield scrapy.Request(
            url=self._get_naver_tv_search_clip_url(1),
            callback=self._parse_search_clip_response
        )

    def _parse_clip_type(self, clip_type):
        if clip_type not in [NAVER_TV_CLIP_TYPE_FULL_GAME, NAVER_TV_CLIP_TYPE_CONDENSED_GAME]:
            raise scrapy.exceptions.NotSupported('Invalid clip_type given')

        return clip_type

    def _parse_team_name(self, team_name):
        if team_name is not None:
            if team_name not in KBO_LEAGUE_TEAM_NAMES_LONG:
                raise scrapy.exceptions.NotSupported('Invalid team_name given')

        return team_name

    def _parse_end_date(self, end_date):
        if end_date:
            return self._parse_date_text(end_date)

        return datetime.datetime.now(KST_TZINFO).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

    def _parse_start_date(self, start_date):
        if start_date:
            return self._parse_date_text(start_date)

        return self.end_date - datetime.timedelta(days=2)

    def _parse_min_clip_length(self, min_clip_length):
        if min_clip_length:
            return int(min_clip_length)

        if self.clip_type == NAVER_TV_CLIP_TYPE_FULL_GAME:
            return 3600

        return None

    def _parse_max_clip_length(self, max_clip_length):
        if max_clip_length:
            return int(max_clip_length)

        if self.clip_type == NAVER_TV_CLIP_TYPE_CONDENSED_GAME:
            return 3600

        return None

    def _parse_max_num_pages(self, max_num_pages):
        if max_num_pages:
            return int(max_num_pages)

        return 1

    def _parse_do_dry_run(self, do_dry_run):
        if do_dry_run:
            if str(do_dry_run).lower() in ['1', 'true']:
                return True

        return False

    def _parse_output_dir_path(self, output_dir_path):
        if self.do_dry_run is False:
            if output_dir_path is None or os.path.exists(output_dir_path) is False:
                raise scrapy.exceptions.NotSupported(
                    'Invalid output_dir_path given (does not exist)'
                )

        return output_dir_path

    def _parse_tmp_dir_path(self, tmp_dir_path):
        if self.do_dry_run is False:
            if tmp_dir_path is None or os.path.exists(tmp_dir_path) is False:
                raise scrapy.exceptions.NotSupported(
                    'Invalid tmp_dir_path given (does not exist)'
                )

        return tmp_dir_path

    def _parse_full_game_feed_path(self, full_game_feed_path):
        if self.clip_type == NAVER_TV_CLIP_TYPE_CONDENSED_GAME:
            if full_game_feed_path is None or os.path.exists(full_game_feed_path) is False:
                raise scrapy.exceptions.NotSupported(
                    'Invalid full_game_feed_path given (does not exist)'
                )

        return full_game_feed_path

    def _parse_search_clip_response(self, response):
        search_results = self._get_search_results(response)

        for search_result in search_results:
            parsed_clip = self._parse_search_result(search_result)

            yield scrapy.Request(
                url=parsed_clip.get('url'),
                callback=self._parse_clip_response,
                cb_kwargs={'parsed_clip': parsed_clip}
            )

        self._increment_num_pages()
        next_page_number = self._get_next_page_number(response)

        if next_page_number:
            yield scrapy.Request(
                self._get_naver_tv_search_clip_url(next_page_number),
                callback=self._parse_search_clip_response
            )

    def _parse_clip_response(self, response, parsed_clip):
        clip_date_text = self._get_clip_date_text(response)
        clip_date_parsed = self._parse_date_text(clip_date_text)

        if clip_date_parsed:
            parsed_clip['year'] = clip_date_parsed.year
            parsed_clip['month'] = clip_date_parsed.month
            parsed_clip['day'] = clip_date_parsed.day

            if self.clip_type == NAVER_TV_CLIP_TYPE_CONDENSED_GAME:
                parsed_clip['away_team_name'] = self._get_away_team_name_from_full_game_feed(
                    parsed_clip.get('home_team_name'),
                    clip_date_parsed
                )

        yield parsed_clip

    def _get_naver_tv_search_clip_url(self, page_number):
        if self.clip_type == NAVER_TV_CLIP_TYPE_FULL_GAME:
            query = NAVER_TV_SEARCH_CLIP_FULL_GAME_QUERY.copy()
        elif self.clip_type == NAVER_TV_CLIP_TYPE_CONDENSED_GAME:
            query = NAVER_TV_SEARCH_CLIP_CONDENSED_GAME_QUERY.copy()

        query['page'] = page_number

        return urllib.parse.urlunparse((
            NAVER_TV_SCHEME,
            NAVER_TV_NETLOC,
            NAVER_TV_SEARCH_CLIP_PATH,
            '',
            urllib.parse.urlencode(
                query,
                quote_via=urllib.parse.quote
            ),
            '',
        ))

    def _parse_search_result(self, search_result):
        if self._is_full_game_search_result(search_result):
            return self._parse_full_game_search_result(search_result)

        if self._is_condensed_game_search_result(search_result):
            return self._parse_condensed_game_search_result(search_result)

        return self._parse_unknown_search_result(search_result)

    def _is_full_game_search_result(self, search_result):
        return NAVER_TV_CLIP_FULL_GAME_TITLE_REGEX.fullmatch(
            self._get_clip_title_text(search_result)
        )

    def _parse_full_game_search_result(self, search_result):
        clip_url_text = self._get_clip_url_text(search_result)
        clip_title_text = self._get_clip_title_text(search_result)
        clip_length_text = self._get_clip_length_text(search_result)
        channel_url_text = self._get_channel_url_text(search_result)

        clip_url_parsed = urllib.parse.urlparse(clip_url_text)
        clip_title_parsed = NAVER_TV_CLIP_FULL_GAME_TITLE_REGEX.match(
            clip_title_text
        )
        clip_length_parsed = self._get_clip_length_parsed(clip_length_text)
        channel_url_parsed = urllib.parse.urlparse(channel_url_text)

        clip_id = self._get_clip_id(clip_url_parsed)
        clip_url = self._get_scrubbed_clip_url(clip_url_parsed)
        home_team_name = KBO_LEAGUE_TEAM_NAME_SHORT_TO_LONG.get(
            clip_title_parsed.group('home_team_name'),
            KBO_LEAGUE_TEAM_NAME_UNKNOWN
        )
        away_team_name = KBO_LEAGUE_TEAM_NAME_SHORT_TO_LONG.get(
            clip_title_parsed.group('away_team_name'),
            KBO_LEAGUE_TEAM_NAME_UNKNOWN
        )

        return NaverTvClip(
            clip_id=clip_id,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url=clip_url,
            length=clip_length_parsed,
            channel_path=channel_url_parsed.path,
            home_team_name=home_team_name,
            away_team_name=away_team_name
        )

    def _is_condensed_game_search_result(self, search_result):
        return NAVER_TV_CLIP_CONDENSED_GAME_TITLE_REGEX.fullmatch(
            self._get_clip_title_text(search_result)
        )

    def _parse_condensed_game_search_result(self, search_result):
        clip_url_text = self._get_clip_url_text(search_result)
        clip_length_text = self._get_clip_length_text(search_result)
        channel_url_text = self._get_channel_url_text(search_result)

        clip_url_parsed = urllib.parse.urlparse(clip_url_text)
        clip_length_parsed = self._get_clip_length_parsed(clip_length_text)
        channel_url_parsed = urllib.parse.urlparse(channel_url_text)

        clip_id = self._get_clip_id(clip_url_parsed)
        clip_url = self._get_scrubbed_clip_url(clip_url_parsed)
        home_team_name = NAVER_TV_CHANNEL_PATH_TO_KBO_LEAGUE_TEAM_NAME_LONG.get(
            channel_url_parsed.path,
            KBO_LEAGUE_TEAM_NAME_UNKNOWN
        )

        return NaverTvClip(
            clip_id=clip_id,
            clip_type=NAVER_TV_CLIP_TYPE_CONDENSED_GAME,
            url=clip_url,
            length=clip_length_parsed,
            channel_path=channel_url_parsed.path,
            home_team_name=home_team_name
        )

    def _parse_unknown_search_result(self, search_result):
        clip_url_text = self._get_clip_url_text(search_result)
        clip_title_text = self._get_clip_title_text(search_result)
        clip_length_text = self._get_clip_length_text(search_result)
        channel_url_text = self._get_channel_url_text(search_result)

        clip_url_parsed = urllib.parse.urlparse(clip_url_text)
        clip_length_parsed = self._get_clip_length_parsed(clip_length_text)
        channel_url_parsed = urllib.parse.urlparse(channel_url_text)

        clip_id = self._get_clip_id(clip_url_parsed)
        clip_url = self._get_scrubbed_clip_url(clip_url_parsed)
        home_team_name = KBO_LEAGUE_TEAM_NAME_UNKNOWN
        away_team_name = KBO_LEAGUE_TEAM_NAME_UNKNOWN

        return NaverTvClip(
            clip_id=clip_id,
            clip_type=NAVER_TV_CLIP_TYPE_UNKNOWN,
            url=clip_url,
            length=clip_length_parsed,
            channel_path=channel_url_parsed.path,
            home_team_name=home_team_name,
            away_team_name=away_team_name
        )

    def _parse_date_text(self, date_text):
        parsed_datetime = dateparser.parse(date_text)

        if parsed_datetime is not None:
            parsed_datetime = parsed_datetime.replace(
                tzinfo=KST_TZINFO
            )

        return parsed_datetime

    def _get_search_results(self, search_clip_response):
        return (
            search_clip_response.css('div#clip_list')
                                .css('div.thl')
                                .css('div.thl_a')
        )

    def _get_clip_length_text(self, search_result):
        return (
            search_result.css('a.cds_thm')
                         .css('span.tm_b::text')
                         .get()
        )

    def _get_clip_title_text(self, search_result):
        return (
            search_result.css('div.inner')
                         .css('dl')
                         .css('dt')
                         .css('a::attr(title)')
                         .get()
        )

    def _get_clip_url_text(self, search_result):
        return (
            search_result.css('div.inner')
                         .css('dl')
                         .css('dt')
                         .css('a::attr(href)')
                         .get()
        )

    def _get_channel_url_text(self, search_result):
        return (
            search_result.css('div.inner')
                         .css('dl')
                         .css('dd')
                         .css('span.ch_txt')
                         .css('a::attr(href)')
                         .get()
        )

    def _get_clip_date_text(self, clip_response):
        return (
            clip_response.css('div#clipInfoArea')
                         .css('div.watch_title')
                         .css('div.title_info')
                         .css('div.title_info')
                         .css('span.date::text')
                         .get()
        )

    def _get_clip_length_parsed(self, clip_length_text):
        clip_length_parts = clip_length_text.split(':')
        clip_length_parts_len = len(clip_length_parts)

        if clip_length_parts_len == 3:
            hours = int(clip_length_parts[0])
            minutes = int(clip_length_parts[1])
            seconds = int(clip_length_parts[2])
        elif clip_length_parts_len == 2:
            hours = 0
            minutes = int(clip_length_parts[0])
            seconds = int(clip_length_parts[1])

        hours_in_seconds = hours * 60 * 60
        minutes_in_seconds = minutes * 60

        return hours_in_seconds + minutes_in_seconds + seconds

    def _get_clip_id(self, clip_url_parsed):
        return clip_url_parsed.path.replace('/v/', '')

    def _get_scrubbed_clip_url(self, clip_url_parsed):
        return urllib.parse.urlunparse((
            NAVER_TV_SCHEME,
            NAVER_TV_NETLOC,
            clip_url_parsed.path,
            '',
            '',
            '',
        ))

    def _get_away_team_name_from_full_game_feed(self,
                                                home_team_name,
                                                clip_date_parsed):
        for row in self._get_full_game_feed():
            is_match = (
                row['home_team_name'] == home_team_name and
                int(row['year']) == clip_date_parsed.year and
                int(row['month']) == clip_date_parsed.month and
                int(row['day']) == clip_date_parsed.day
            )

            if is_match:
                return row['away_team_name']

        return KBO_LEAGUE_TEAM_NAME_UNKNOWN

    def _get_full_game_feed(self):
        if self._full_game_feed is None:
            with open(self.full_game_feed_path) as csv_file:
                csv_reader = csv.DictReader(csv_file)
                self._full_game_feed = [row for row in csv_reader]

        return self._full_game_feed

    def _increment_num_pages(self):
        if self._num_pages is None:
            self._num_pages = 0

        self._num_pages = self._num_pages + 1

    def _get_next_page_number(self, search_clip_response):
        paging = self._get_paging(search_clip_response)
        current_page_number = self._get_current_page_number(paging)
        last_page_number = self._get_last_page_number(paging)

        if current_page_number == last_page_number:
            return None

        if self._num_pages == self.max_num_pages:
            return None

        return current_page_number + 1

    def _get_paging(self, search_clip_response):
        return (
            search_clip_response.css('div#clipPaging')
                                .css('div.paging_wrap')
        )

    def _get_current_page_number(self, paging):
        return int(
            paging.css('strong.page')
                  .css('span.num::text')
                  .get()
        )

    def _get_last_page_number(self, paging):
        return int(
            paging.css('a.next_end::attr(data-page)')
                  .get()
        )
