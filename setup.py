from setuptools import setup, find_namespace_packages


setup(
    name='kbo',
    version='0.1',
    packages=find_namespace_packages(include=["kbo.*"]),
    install_requires=[
        'Scrapy==2.1.0',
        'dateparser==0.7.4',
        'ffmpeg==1.4',
        'mutagen==1.44.0',
        'youtube_dl==2020.5.8'
    ],
    entry_points={'scrapy': ['settings = kbo.settings']}
)
