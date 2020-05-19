# -*- coding: utf-8 -*-

import datetime
import tempfile
from unittest import TestCase

from kbo.constants import (
    KST_TZINFO,
    NAVER_TV_CLIP_TYPE_CONDENSED_GAME,
    NAVER_TV_CLIP_TYPE_FULL_GAME
)
from kbo.spiders.naver_tv import NaverTvSpider


class NaverTvSpiderTestCase(TestCase):

    def test_default_options_for_full_game_clip_type(self):
        today_kst = datetime.datetime.now(KST_TZINFO).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
        two_days_ago_kst = today_kst - datetime.timedelta(days=2)

        with tempfile.TemporaryDirectory() as output_dir_path:
            with tempfile.TemporaryDirectory() as tmp_dir_path:
                spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )

        self.assertEqual(NAVER_TV_CLIP_TYPE_FULL_GAME, spider.clip_type)
        self.assertIsNone(spider.team_name)
        self.assertEqual(today_kst, spider.end_date)
        self.assertEqual(two_days_ago_kst, spider.start_date)
        self.assertEqual(3600, spider.min_clip_length)
        self.assertIsNone(spider.max_clip_length)
        self.assertEqual(1, spider.max_num_pages)
        self.assertEqual(output_dir_path, spider.output_dir_path)
        self.assertEqual(tmp_dir_path, spider.tmp_dir_path)
        self.assertIsNone(spider.full_game_feed_path)
        self.assertFalse(spider.do_dry_run)

    def test_default_options_for_full_game_clip_type(self):
        today_kst = datetime.datetime.now(KST_TZINFO).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
        two_days_ago_kst = today_kst - datetime.timedelta(days=2)

        with tempfile.TemporaryDirectory() as output_dir_path:
            with tempfile.TemporaryDirectory() as tmp_dir_path:
                with tempfile.NamedTemporaryFile(dir=tmp_dir_path) as full_game_feed_path_file:
                    spider = NaverTvSpider(
                        clip_type=NAVER_TV_CLIP_TYPE_CONDENSED_GAME,
                        output_dir_path=output_dir_path,
                        tmp_dir_path=tmp_dir_path,
                        full_game_feed_path=full_game_feed_path_file.name
                    )

        self.assertEqual(NAVER_TV_CLIP_TYPE_CONDENSED_GAME, spider.clip_type)
        self.assertIsNone(spider.team_name)
        self.assertEqual(today_kst, spider.end_date)
        self.assertEqual(two_days_ago_kst, spider.start_date)
        self.assertIsNone(spider.min_clip_length)
        self.assertEqual(3600, spider.max_clip_length)
        self.assertEqual(1, spider.max_num_pages)
        self.assertEqual(output_dir_path, spider.output_dir_path)
        self.assertEqual(tmp_dir_path, spider.tmp_dir_path)
        self.assertEqual(full_game_feed_path_file.name, spider.full_game_feed_path)
        self.assertFalse(spider.do_dry_run)

    def test_sets_team_name(self):
        with tempfile.TemporaryDirectory() as output_dir_path:
            with tempfile.TemporaryDirectory() as tmp_dir_path:
                spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    team_name='KT Wiz',
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )

        self.assertEqual('KT Wiz', spider.team_name)

    def test_sets_start_date(self):
        with tempfile.TemporaryDirectory() as output_dir_path:
            with tempfile.TemporaryDirectory() as tmp_dir_path:
                spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    start_date='2020/05/16',
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )

        self.assertEqual(
            datetime.datetime(2020, 5, 16, tzinfo=KST_TZINFO),
            spider.start_date
        )

    def test_sets_end_date(self):
        with tempfile.TemporaryDirectory() as output_dir_path:
            with tempfile.TemporaryDirectory() as tmp_dir_path:
                spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    end_date='2020/05/16',
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )

        self.assertEqual(
            datetime.datetime(2020, 5, 14, tzinfo=KST_TZINFO),
            spider.start_date
        )
        self.assertEqual(
            datetime.datetime(2020, 5, 16, tzinfo=KST_TZINFO),
            spider.end_date
        )

    def test_sets_min_clip_length(self):
        with tempfile.TemporaryDirectory() as output_dir_path:
            with tempfile.TemporaryDirectory() as tmp_dir_path:
                spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    min_clip_length=1234,
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )

        self.assertEqual(1234, spider.min_clip_length)

    def test_sets_max_clip_length(self):
        with tempfile.TemporaryDirectory() as output_dir_path:
            with tempfile.TemporaryDirectory() as tmp_dir_path:
                spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    max_clip_length=1234,
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )

        self.assertEqual(1234, spider.max_clip_length)

    def test_sets_max_num_pages(self):
        with tempfile.TemporaryDirectory() as output_dir_path:
            with tempfile.TemporaryDirectory() as tmp_dir_path:
                spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    max_num_pages=1234,
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )

        self.assertEqual(1234, spider.max_num_pages)

    def test_sets_do_dry_run(self):
        with tempfile.TemporaryDirectory() as output_dir_path:
            with tempfile.TemporaryDirectory() as tmp_dir_path:
                first_spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    do_dry_run=True,
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )
                second_spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    do_dry_run='true',
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )
                third_spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    do_dry_run=1,
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )
                fourth_spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    do_dry_run='1',
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )
                fifth_spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    do_dry_run=0,
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )
                sixth_spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    do_dry_run='0',
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )
                seventh_spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    do_dry_run=False,
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )
                eighth_spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    do_dry_run='false',
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )

        self.assertTrue(first_spider.do_dry_run)
        self.assertTrue(second_spider.do_dry_run)
        self.assertTrue(third_spider.do_dry_run)
        self.assertTrue(fourth_spider.do_dry_run)
        self.assertFalse(fifth_spider.do_dry_run)
        self.assertFalse(sixth_spider.do_dry_run)
        self.assertFalse(seventh_spider.do_dry_run)
        self.assertFalse(eighth_spider.do_dry_run)
