# -*- coding: utf-8 -*-

import datetime
import os
import pathlib
import shutil

import ffmpeg
from mutagen.mp4 import MP4
from scrapy.exceptions import DropItem
import youtube_dl

from kbo.constants import (
    CONDENSED_GAME_CLIP_FILENAME_TEMPLATE,
    CONDENSED_GAME_CLIP_THUMBNAIL_FILENAME_TEMPLATE,
    CONDENSED_GAME_CLIP_TITLE_TEMPLATE,
    FULL_GAME_CLIP_FILENAME_TEMPLATE,
    FULL_GAME_CLIP_THUMBNAIL_FILENAME_TEMPLATE,
    FULL_GAME_CLIP_TITLE_TEMPLATE,
    GAME_CLIP_DATE_RELEASED_TEMPLATE,
    GAME_CLIP_SHOW_NAME,
    GAME_CLIP_THUMBNAIL_TIMESTAMP,
    KBO_LEAGUE_TEAM_NAME_UNKNOWN,
    KST_TZINFO,
    MUTAGEN_TAG_ARTIST_KEY,
    MUTAGEN_TAG_DATE_RELEASED_KEY,
    MUTAGEN_TAG_TITLE_KEY,
    MUTAGEN_TAG_TV_SHOW_KEY,
    NAVER_TV_CHANNEL_PATHS,
    NAVER_TV_CLIP_TYPE_CONDENSED_GAME,
    NAVER_TV_CLIP_TYPE_FULL_GAME,
    NAVER_TV_CLIP_TYPE_UNKNOWN
)


class ClipValidationPipeline:

    def process_item(self, item, spider):
        self._validate_clip_type(item, spider)
        self._validate_clip_length(item, spider)
        self._validate_channel_path(item)
        self._validate_clip_date(item, spider)
        self._validate_team_names(item, spider)

        return item

    def _validate_clip_type(self, item, spider):
        if item.get('clip_type') != spider.clip_type:
            raise DropItem(
                "Clip type ({clip_type}) does not match {target_clip_type}".format(
                    clip_type=item.get('clip_type'),
                    target_clip_type=spider.clip_type
                )
            )

    def _validate_clip_length(self, item, spider):
        if spider.min_clip_length is not None:
            if item.get('length') < spider.min_clip_length:
                raise DropItem(
                    "Clip length ({clip_length} seconds) shorter than {target_min_clip_length} seconds".format(
                        clip_length=item.get('length'),
                        target_min_clip_length=spider.min_clip_length
                    )
                )

        if spider.max_clip_length is not None:
            if item.get('length') > spider.max_clip_length:
                raise DropItem(
                    "Clip length ({clip_length} seconds) longer than {target_max_clip_length} seconds".format(
                        clip_length=item.get('length'),
                        target_max_clip_length=spider.max_clip_length
                    )
                )

    def _validate_channel_path(self, item):
        if item.get('channel_path') not in NAVER_TV_CHANNEL_PATHS:
            raise DropItem(
                "Clip channel ({clip_channel_path}) is not a KBO League team channel".format(
                    clip_channel_path=item.get('channel_path')
                )
            )

    def _validate_clip_date(self, item, spider):
        if None in [item.get('year'), item.get('month'), item.get('day')]:
            raise DropItem('Clip date unknown')

        item_datetime = datetime.datetime(
            year=item.get('year'),
            month=item.get('month'),
            day=item.get('day'),
            tzinfo=KST_TZINFO
        )

        date_range_match = (
            item_datetime >= spider.start_date and
            item_datetime <= spider.end_date
        )

        if date_range_match is False:
            raise DropItem(
                "Clip date ({clip_date}) not within target date range ({target_start_date} - {target_end_date})".format(
                    clip_date=item_datetime.strftime('%x'),
                    target_start_date=spider.start_date.strftime('%x'),
                    target_end_date=spider.end_date.strftime('%x')
                )
            )

    def _validate_team_names(self, item, spider):
        if item.get('home_team_name') == KBO_LEAGUE_TEAM_NAME_UNKNOWN:
            raise DropItem('Home team name unknown')

        if item.get('away_team_name') == KBO_LEAGUE_TEAM_NAME_UNKNOWN:
            raise DropItem('Away team name unknown')

        team_name_match = (
            spider.team_name is None or
            spider.team_name in [
                item.get('home_team_name'),
                item.get('away_team_name')
            ]
        )

        if team_name_match is False:
            raise DropItem(
                "Target team name {team_name} does not match clip team names (home: {home_team_name}, away: {away_team_name})".format(
                    team_name=spider.team_name,
                    home_team_name=item.get('home_team_name'),
                    away_team_name=item.get('away_team_name')
                )
            )


class ClipDownloadPipeline:

    def process_item(self, item, spider):
        if self._should_download_clip(item, spider):
            self._download_clip(item, spider)

        return item

    def _should_download_clip(self, item, spider):
        if spider.do_dry_run is True:
            return False

        if os.path.exists(_get_clip_file_path(item, spider.tmp_dir_path)) is True:
            return False

        if os.path.exists(_get_clip_file_path(item, spider.output_dir_path)) is True:
            return False

        return True

    def _download_clip(self, item, spider):
        ydl_options = {
            'logger': spider.logger,
            'outtmpl': _get_clip_file_path(
                item,
                spider.tmp_dir_path
            )
        }

        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            ydl.download([item.get('url')])


class ClipTagPipeline:

    def process_item(self, item, spider):
        if self._should_tag_clip(item, spider):
            self._tag_clip(item, spider)

        return item

    def _should_tag_clip(self, item, spider):
        if spider.do_dry_run is True:
            return False

        if os.path.exists(_get_clip_file_path(item, spider.tmp_dir_path)) is False:
            return False

        return True

    def _tag_clip(self, item, spider):
        clip_file = MP4(_get_clip_file_path(item, spider.tmp_dir_path))
        clip_file.tags[MUTAGEN_TAG_ARTIST_KEY] = GAME_CLIP_SHOW_NAME
        clip_file.tags[MUTAGEN_TAG_TV_SHOW_KEY] = GAME_CLIP_SHOW_NAME
        clip_file.tags[MUTAGEN_TAG_TITLE_KEY] = _get_clip_title(item)
        clip_file.tags[MUTAGEN_TAG_DATE_RELEASED_KEY] = _get_clip_date_released(item)
        clip_file.save()


class ClipThumbnailPipeline:

    def process_item(self, item, spider):
        if self._should_create_thumbnail(item, spider):
            self._create_thumbnail(item, spider)

        return item

    def _should_create_thumbnail(self, item, spider):
        if spider.do_dry_run is True:
            return False

        if os.path.exists(_get_clip_file_path(item, spider.tmp_dir_path)) is False:
            return False

        if os.path.exists(_get_clip_thumbnail_file_path(item, spider.tmp_dir_path)) is True:
            return False

        if os.path.exists(_get_clip_thumbnail_file_path(item, spider.output_dir_path)) is True:
            return False

        return True

    def _create_thumbnail(self, item, spider):
        input_path = _get_clip_file_path(item, spider.tmp_dir_path)
        output_path = _get_clip_thumbnail_file_path(item, spider.tmp_dir_path)

        try:
            ffmpeg_chain = ffmpeg.input(
                input_path,
                ss=GAME_CLIP_THUMBNAIL_TIMESTAMP
            )
            ffmpeg_chain = ffmpeg_chain.filter('scale', 640, -1)
            ffmpeg_chain = ffmpeg_chain.output(output_path, vframes=1)
            ffmpeg_chain = ffmpeg_chain.run(capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            raise DropItem(
                "Could not create thumbnail: {ffmpeg_error}".format(
                    ffmpeg_error=e.stderr.decode()
                )
            )


class ClipMovePipeline:

    def process_item(self, item, spider):
        if self._should_move_clip_file(item, spider):
            self._move_clip_file(item, spider)

        if self._should_move_clip_thumbnail_file(item, spider):
            self._move_clip_thumbnail_file(item, spider)

        return item

    def _should_move_clip_file(self, item, spider):
        if spider.do_dry_run is True:
            return False

        if spider.tmp_dir_path == spider.output_dir_path:
            return False

        if os.path.exists(_get_clip_file_path(item, spider.tmp_dir_path)) is False:
            return False

        if os.path.exists(_get_clip_file_path(item, spider.output_dir_path)) is True:
            return False

        return True

    def _move_clip_file(self, item, spider):
        shutil.move(
            _get_clip_file_path(item, spider.tmp_dir_path),
            _get_clip_file_path(item, spider.output_dir_path)
        )

    def _should_move_clip_thumbnail_file(self, item, spider):
        if spider.do_dry_run is True:
            return False

        if spider.tmp_dir_path == spider.output_dir_path:
            return False

        if os.path.exists(_get_clip_thumbnail_file_path(item, spider.tmp_dir_path)) is False:
            return False

        if os.path.exists(_get_clip_thumbnail_file_path(item, spider.output_dir_path)) is True:
            return False

        return True

    def _move_clip_thumbnail_file(self, item, spider):
        shutil.move(
            _get_clip_thumbnail_file_path(item, spider.tmp_dir_path),
            _get_clip_thumbnail_file_path(item, spider.output_dir_path)
        )


def _get_clip_file_path(item, dir_path):
    if item.get('clip_type') == NAVER_TV_CLIP_TYPE_FULL_GAME:
        file_path = _get_full_game_clip_file_path(item, dir_path)
    elif item.get('clip_type') == NAVER_TV_CLIP_TYPE_CONDENSED_GAME:
        file_path = _get_condensed_game_clip_file_path(item, dir_path)

    return file_path


def _get_full_game_clip_file_path(item, dir_path):
    return os.path.join(
        dir_path,
        FULL_GAME_CLIP_FILENAME_TEMPLATE.format(
            clip_id=item.get('clip_id'),
            home_team_name=item.get('home_team_name'),
            away_team_name=item.get('away_team_name'),
            year=item.get('year'),
            month=item.get('month'),
            day=item.get('day')
        )
    )


def _get_condensed_game_clip_file_path(item, dir_path):
    return os.path.join(
        dir_path,
        CONDENSED_GAME_CLIP_FILENAME_TEMPLATE.format(
            clip_id=item.get('clip_id'),
            home_team_name=item.get('home_team_name'),
            away_team_name=item.get('away_team_name'),
            year=item.get('year'),
            month=item.get('month'),
            day=item.get('day')
        )
    )


def _get_clip_title(item):
    if item.get('clip_type') == NAVER_TV_CLIP_TYPE_FULL_GAME:
        title = _get_full_game_clip_title(item)
    elif item.get('clip_type') == NAVER_TV_CLIP_TYPE_CONDENSED_GAME:
        title = _get_condensed_game_clip_title(item)

    return title


def _get_full_game_clip_title(item):
    return FULL_GAME_CLIP_TITLE_TEMPLATE.format(
        home_team_name=item.get('home_team_name'),
        away_team_name=item.get('away_team_name')
    )


def _get_condensed_game_clip_title(item):
    return CONDENSED_GAME_CLIP_TITLE_TEMPLATE.format(
        home_team_name=item.get('home_team_name'),
        away_team_name=item.get('away_team_name')
    )


def _get_clip_date_released(item):
    return GAME_CLIP_DATE_RELEASED_TEMPLATE.format(
        year=item.get('year'),
        month=item.get('month'),
        day=item.get('day')
    )


def _get_clip_thumbnail_file_path(item, dir_path):
    if item.get('clip_type') == NAVER_TV_CLIP_TYPE_FULL_GAME:
        file_path = _get_full_game_clip_thumbnail_file_path(item, dir_path)
    elif item.get('clip_type') == NAVER_TV_CLIP_TYPE_CONDENSED_GAME:
        file_path = _get_condensed_game_clip_thumbnail_file_path(item, dir_path)

    return file_path


def _get_full_game_clip_thumbnail_file_path(item, dir_path):
    return os.path.join(
        dir_path,
        FULL_GAME_CLIP_THUMBNAIL_FILENAME_TEMPLATE.format(
            clip_id=item.get('clip_id'),
            home_team_name=item.get('home_team_name'),
            away_team_name=item.get('away_team_name'),
            year=item.get('year'),
            month=item.get('month'),
            day=item.get('day')
        )
    )


def _get_condensed_game_clip_thumbnail_file_path(item, dir_path):
    return os.path.join(
        dir_path,
        CONDENSED_GAME_CLIP_THUMBNAIL_FILENAME_TEMPLATE.format(
            clip_id=item.get('clip_id'),
            home_team_name=item.get('home_team_name'),
            away_team_name=item.get('away_team_name'),
            year=item.get('year'),
            month=item.get('month'),
            day=item.get('day')
        )
    )
