# -*- coding: utf-8 -*-
"""Playback-scoped detector adapters. No cached timestamps or library ID lookup."""
from resources.lib.introdb import IntroDBAdapter
from resources.lib.chapters import ChaptersAdapter


class Identifier:
    def __init__(self):
        self.introdb_adapter = IntroDBAdapter()
        self.chapter_adapter = ChaptersAdapter()
        self.segment_evidence = {}
