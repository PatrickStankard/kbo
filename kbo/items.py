# -*- coding: utf-8 -*-

import scrapy


class NaverTvClip(scrapy.Item):
    clip_id = scrapy.Field()
    clip_type = scrapy.Field()
    url = scrapy.Field()
    length = scrapy.Field()
    channel_path = scrapy.Field()
    home_team_name = scrapy.Field()
    away_team_name = scrapy.Field()
    year = scrapy.Field()
    month = scrapy.Field()
    day = scrapy.Field()
