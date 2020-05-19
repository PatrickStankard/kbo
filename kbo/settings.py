# -*- coding: utf-8 -*-

BOT_NAME = 'kbo'

SPIDER_MODULES = ['kbo.spiders']
NEWSPIDER_MODULE = 'kbo.spiders'

ROBOTSTXT_OBEY = False

ITEM_PIPELINES = {
    'kbo.pipelines.ClipValidationPipeline': 100,
    'kbo.pipelines.ClipDownloadPipeline': 200,
    'kbo.pipelines.ClipTagPipeline': 300,
    'kbo.pipelines.ClipThumbnailPipeline': 400,
    'kbo.pipelines.ClipMovePipeline': 500
}

COOKIES_ENABLED = False
