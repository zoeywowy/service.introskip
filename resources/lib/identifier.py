# -*- coding: utf-8 -*-
"""Playback-scoped detector adapters and shared community data providers."""
from resources.lib.introdb import IntroDBAdapter
from resources.lib.introdb_open_data import IntroDBOpenDataAdapter
from resources.lib.theintrodb import TheIntroDBAdapter
from resources.lib.chapters import ChaptersAdapter


class Identifier:
    def __init__(self):
        self.introdb_adapter = IntroDBAdapter()
        self.introdb_open_data = IntroDBOpenDataAdapter()
        self.theintrodb_adapter = TheIntroDBAdapter()
        self.chapter_adapter = ChaptersAdapter()
        self.segment_evidence = {}
