# -*- coding: utf-8 -*-

import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

import scrapy

from kbo.constants import (
    KBO_LEAGUE_TEAM_NAME_UNKNOWN,
    NAVER_TV_CLIP_TYPE_CONDENSED_GAME,
    NAVER_TV_CLIP_TYPE_FULL_GAME
)
from kbo.items import NaverTvClip
from kbo.pipelines import (
   ClipValidationPipeline,
   ClipDownloadPipeline,
   ClipTagPipeline,
   ClipThumbnailPipeline,
   ClipMovePipeline
)
from kbo.spiders.naver_tv import NaverTvSpider


class ClipValidationPipelineTestCase(TestCase):

    def test_returns_item_when_processed(self):
        item = NaverTvClip(
            clip_id=13820293,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url='https://tv.naver.com/v/13820293',
            length=15813,
            channel_path='/wyvernsvod',
            home_team_name='SK Wyverns',
            away_team_name='NC Dinos',
            year=2020,
            month=5,
            day=16
        )
        spider = NaverTvSpider(
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            start_date='2020-05-16',
            end_date='2020-05-16',
            do_dry_run=True
        )
        pipeline = ClipValidationPipeline()

        result = pipeline.process_item(item, spider)

        self.assertEqual(item, result)

    def test_raises_drop_item_when_clip_type_does_not_match_target(self):
        item = NaverTvClip(
            clip_id=13875922,
            clip_type=NAVER_TV_CLIP_TYPE_CONDENSED_GAME,
            url='https://tv.naver.com/v/13875922',
            length=620,
            channel_path='/bearsvod',
            home_team_name='Doosan Bears',
            away_team_name='NC Dinos',
            year=2020,
            month=5,
            day=19
        )
        spider = NaverTvSpider(
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            start_date='2020-05-19',
            end_date='2020-05-19',
            do_dry_run=True
        )
        pipeline = ClipValidationPipeline()

        with self.assertRaisesRegex(scrapy.exceptions.DropItem, '^Clip type'):
            pipeline.process_item(item, spider)

    def test_raises_drop_item_when_clip_length_is_too_short(self):
        item = NaverTvClip(
            clip_id=13820293,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url='https://tv.naver.com/v/13820293',
            length=15813,
            channel_path='/wyvernsvod',
            home_team_name='SK Wyverns',
            away_team_name='NC Dinos',
            year=2020,
            month=5,
            day=16
        )
        spider = NaverTvSpider(
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            start_date='2020-05-16',
            end_date='2020-05-16',
            min_clip_length=16000,
            do_dry_run=True
        )
        pipeline = ClipValidationPipeline()

        with self.assertRaisesRegex(scrapy.exceptions.DropItem, '^Clip length'):
            pipeline.process_item(item, spider)

    def test_raises_drop_item_when_clip_length_is_too_long(self):
        item = NaverTvClip(
            clip_id=13820293,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url='https://tv.naver.com/v/13820293',
            length=15813,
            channel_path='/wyvernsvod',
            home_team_name='SK Wyverns',
            away_team_name='NC Dinos',
            year=2020,
            month=5,
            day=16
        )
        spider = NaverTvSpider(
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            start_date='2020-05-16',
            end_date='2020-05-16',
            max_clip_length=1600,
            do_dry_run=True
        )
        pipeline = ClipValidationPipeline()

        with self.assertRaisesRegex(scrapy.exceptions.DropItem, '^Clip length'):
            pipeline.process_item(item, spider)

    def test_raises_drop_item_when_channel_path_is_invalid(self):
        item = NaverTvClip(
            clip_id=13820293,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url='https://tv.naver.com/v/13820293',
            length=15813,
            channel_path='/kbofanpage',
            home_team_name='SK Wyverns',
            away_team_name='NC Dinos',
            year=2020,
            month=5,
            day=16
        )
        spider = NaverTvSpider(
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            start_date='2020-05-16',
            end_date='2020-05-16',
            do_dry_run=True
        )
        pipeline = ClipValidationPipeline()

        with self.assertRaises(scrapy.exceptions.DropItem):
            pipeline.process_item(item, spider)

    def test_raises_drop_item_when_clip_date_unknown(self):
        item = NaverTvClip(
            clip_id=13820293,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url='https://tv.naver.com/v/13820293',
            length=15813,
            channel_path='/wyvernsvod',
            home_team_name='SK Wyverns',
            away_team_name='NC Dinos',
            year=None,
            month=None,
            day=None
        )
        spider = NaverTvSpider(
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            start_date='2020-05-16',
            end_date='2020-05-16',
            do_dry_run=True
        )
        pipeline = ClipValidationPipeline()

        with self.assertRaisesRegex(scrapy.exceptions.DropItem, '^Clip date'):
            pipeline.process_item(item, spider)

    def test_raises_drop_item_when_clip_date_before_date_range(self):
        item = NaverTvClip(
            clip_id=13820293,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url='https://tv.naver.com/v/13820293',
            length=15813,
            channel_path='/wyvernsvod',
            home_team_name='SK Wyverns',
            away_team_name='NC Dinos',
            year=2020,
            month=5,
            day=16
        )
        spider = NaverTvSpider(
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            start_date='2020-05-17',
            end_date='2020-05-19',
            do_dry_run=True
        )
        pipeline = ClipValidationPipeline()

        with self.assertRaisesRegex(scrapy.exceptions.DropItem, '^Clip date'):
            pipeline.process_item(item, spider)

    def test_raises_drop_item_when_clip_date_after_date_range(self):
        item = NaverTvClip(
            clip_id=13820293,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url='https://tv.naver.com/v/13820293',
            length=15813,
            channel_path='/wyvernsvod',
            home_team_name='SK Wyverns',
            away_team_name='NC Dinos',
            year=2020,
            month=5,
            day=16
        )
        spider = NaverTvSpider(
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            start_date='2020-05-15',
            end_date='2020-05-13',
            do_dry_run=True
        )
        pipeline = ClipValidationPipeline()

        with self.assertRaisesRegex(scrapy.exceptions.DropItem, '^Clip date'):
            pipeline.process_item(item, spider)

    def test_raises_drop_item_when_home_team_name_unknown(self):
        item = NaverTvClip(
            clip_id=13820293,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url='https://tv.naver.com/v/13820293',
            length=15813,
            channel_path='/wyvernsvod',
            home_team_name=KBO_LEAGUE_TEAM_NAME_UNKNOWN,
            away_team_name='NC Dinos',
            year=2020,
            month=5,
            day=16
        )
        spider = NaverTvSpider(
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            start_date='2020-05-16',
            end_date='2020-05-16',
            do_dry_run=True
        )
        pipeline = ClipValidationPipeline()

        with self.assertRaisesRegex(scrapy.exceptions.DropItem, '^Home team name'):
            pipeline.process_item(item, spider)

    def test_raises_drop_item_when_away_team_name_unknown(self):
        item = NaverTvClip(
            clip_id=13820293,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url='https://tv.naver.com/v/13820293',
            length=15813,
            channel_path='/wyvernsvod',
            home_team_name='SK Wyverns',
            away_team_name=KBO_LEAGUE_TEAM_NAME_UNKNOWN,
            year=2020,
            month=5,
            day=16
        )
        spider = NaverTvSpider(
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            start_date='2020-05-16',
            end_date='2020-05-16',
            do_dry_run=True
        )
        pipeline = ClipValidationPipeline()

        with self.assertRaisesRegex(scrapy.exceptions.DropItem, '^Away team name'):
            pipeline.process_item(item, spider)

    def test_raises_drop_item_when_team_names_do_not_match_target(self):
        item = NaverTvClip(
            clip_id=13820293,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url='https://tv.naver.com/v/13820293',
            length=15813,
            channel_path='/wyvernsvod',
            home_team_name='SK Wyverns',
            away_team_name='NC Dinos',
            year=2020,
            month=5,
            day=16
        )
        spider = NaverTvSpider(
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            team_name='KT Wiz',
            start_date='2020-05-16',
            end_date='2020-05-16',
            do_dry_run=True
        )
        pipeline = ClipValidationPipeline()

        with self.assertRaisesRegex(scrapy.exceptions.DropItem, '^Target team name'):
            pipeline.process_item(item, spider)


class ClipDownloadPipelineTestCase(TestCase):

    def test_returns_item_when_processed(self):
        item = NaverTvClip(
            clip_id=13820293,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url='https://tv.naver.com/v/13820293',
            length=15813,
            channel_path='/wyvernsvod',
            home_team_name='SK Wyverns',
            away_team_name='NC Dinos',
            year=2020,
            month=5,
            day=16
        )
        with tempfile.TemporaryDirectory() as output_dir_path:
            with tempfile.TemporaryDirectory() as tmp_dir_path:
                spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    start_date='2020-05-16',
                    end_date='2020-05-16',
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )
                pipeline = ClipDownloadPipeline()

                with patch('youtube_dl.YoutubeDL') as youtube_dl_mock:
                    result = pipeline.process_item(item, spider)

        args, _ = youtube_dl_mock.call_args
        self.assertEqual(item, result)
        self.assertEqual(
            os.path.join(
                tmp_dir_path,
                'KBO League - S2020E13820293 - 2020.05.16 - NC Dinos at SK Wyverns.mp4'
            ),
            args[0]['outtmpl']
        )

    def test_skips_download_on_dry_run(self):
        item = NaverTvClip(
            clip_id=13820293,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url='https://tv.naver.com/v/13820293',
            length=15813,
            channel_path='/wyvernsvod',
            home_team_name='SK Wyverns',
            away_team_name='NC Dinos',
            year=2020,
            month=5,
            day=16
        )
        spider = NaverTvSpider(
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            start_date='2020-05-16',
            end_date='2020-05-16',
            do_dry_run=True
        )
        pipeline = ClipDownloadPipeline()

        with patch('youtube_dl.YoutubeDL') as youtube_dl_mock:
            result = pipeline.process_item(item, spider)

        self.assertEqual(item, result)
        youtube_dl_mock.assert_not_called()


class ClipThumbnailPipelineTestCase(TestCase):

    def test_skips_thumbnail_on_dry_run(self):
        item = NaverTvClip(
            clip_id=13820293,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url='https://tv.naver.com/v/13820293',
            length=15813,
            channel_path='/wyvernsvod',
            home_team_name='SK Wyverns',
            away_team_name='NC Dinos',
            year=2020,
            month=5,
            day=16
        )
        with tempfile.TemporaryDirectory() as output_dir_path:
            with tempfile.TemporaryDirectory() as tmp_dir_path:
                spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    start_date='2020-05-16',
                    end_date='2020-05-16',
                    do_dry_run=True,
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )
                pipeline = ClipThumbnailPipeline()

                with patch('ffmpeg.input') as ffmpeg_input_mock:
                    result = pipeline.process_item(item, spider)

        self.assertEqual(item, result)
        ffmpeg_input_mock.assert_not_called()


class ClipMovePipelineTestCase(TestCase):

    def test_skips_move_on_dry_run(self):
        item = NaverTvClip(
            clip_id=13820293,
            clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
            url='https://tv.naver.com/v/13820293',
            length=15813,
            channel_path='/wyvernsvod',
            home_team_name='SK Wyverns',
            away_team_name='NC Dinos',
            year=2020,
            month=5,
            day=16
        )
        with tempfile.TemporaryDirectory() as output_dir_path:
            with tempfile.TemporaryDirectory() as tmp_dir_path:
                spider = NaverTvSpider(
                    clip_type=NAVER_TV_CLIP_TYPE_FULL_GAME,
                    start_date='2020-05-16',
                    end_date='2020-05-16',
                    do_dry_run=True,
                    output_dir_path=output_dir_path,
                    tmp_dir_path=tmp_dir_path
                )
                pipeline = ClipMovePipeline()

                with patch('shutil.move') as move_mock:
                    result = pipeline.process_item(item, spider)

        self.assertEqual(item, result)
        move_mock.assert_not_called()
