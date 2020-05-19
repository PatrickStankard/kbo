# kbo

A [Scrapy](https://scrapy.org/) project to archive full and condensed [KBO League](https://en.wikipedia.org/wiki/KBO_League) games from [Naver TV](https://tv.naver.com/).

## Prerequisites

- [Python >= 3.5](https://www.python.org/downloads/)
- [FFmpeg](https://ffmpeg.org/)

## Installation

To install the project dependencies, from the root of the project, run:

```bash
$ pip install .
```

## Usage

The pipeline for archiving full and condensed games includes:

- Downloading the video (via [youtube-dl](https://ytdl-org.github.io/youtube-dl/index.html))
- Tagging the video (via [Mutagen](https://mutagen.readthedocs.io/en/latest/))
- Creating a thumbnail image of the video (via [FFmpeg](https://ffmpeg.org/))

This pipeline is optimized for serving the videos via [Plex Media Server](https://www.plex.tv/), without spoiling the outcome of the game.

### Archiving Full Games

```bash
$ scrapy crawl naver_tv \
    -a clip_type='full_game' # required \
    -a output_dir_path='/path/to/output/dir' # required: final destination of archived games \
    -a tmp_dir_path='/path/to/tmp/dir' # required: temporary working directory \
    -a team_name='KT Wiz' # optional \
    -a end_date='2020-05-15' # optional: defaults to today (in KST) \
    -a start_date='2020-05-13' # optional: defaults to two days before end_date value (in KST) \
    -a min_clip_length=5000 # optional: defaults to 3600 when clip_type='full_game' (in seconds) \
    -a max_clip_length=10000 # optional (in seconds) \
    -a max_num_pages=5 # optional: maximum number of search result pages to iterate over, defaults to 1 \
    -a do_dry_run='true' # optional: skips downloading the video, defaults to 'false' \
    -o '/path/to/full_game_feed.csv' # optional: save the item feed as a CSV (required for condensed_game crawl)
```

### Archiving Condensed Games

In order to archive condensed games, the CSV feed of a full game crawl is required.
For best results, you should also use the same values that were used for `team_name`,
`end_date`, `start_date`, and `max_num_pages`.

```bash
$ scrapy crawl naver_tv \
    -a clip_type='condensed_game' # required \
    -a full_game_feed_path='/path/to/full_game_feed.csv' # required: item feed from previous full_game crawl \
    -a tmp_dir_path='/path/to/tmp/dir' # required: temporary working directory \
    -a output_dir_path='/path/to/output/dir' # required: final destination of archived games \
    -a team_name='KT Wiz' # optional: should match value from previous full_game crawl \
    -a end_date='2020-05-15' # optional: defaults to today (in KST). should match value from previous full_game crawl \
    -a start_date='2020-05-13' # optional: defaults to two days before end_date value (in KST). should match value from previous full_game crawl \
    -a min_clip_length='5000' # optional (in seconds) \
    -a max_clip_length='10000' # optional: defaults to 3600 when clip_type='condensed_game' (in seconds) \
    -a max_num_pages=5 # optional: maximum number of search result pages to iterate over, defaults to 1. should match value from previous full_game crawl \
    -a do_dry_run='true' # optional: skips downloading the video, defaults to 'false' \
    -o '/path/to/condensed_game_feed.csv' # optional: save the item feed as a CSV
```
