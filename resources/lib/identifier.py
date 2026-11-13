# -*- coding: utf-8 -*-
"""Playback-scoped detector adapters with lazy loading for the bulk data index."""
from resources.lib.introdb import IntroDBAdapter
from resources.lib.theintrodb import TheIntroDBAdapter
from resources.lib.chapters import ChaptersAdapter


class Identifier:
    def __init__(self):
        self.introdb_adapter = IntroDBAdapter()
        self.theintrodb_adapter = TheIntroDBAdapter()
        self.chapter_adapter = ChaptersAdapter()
        self._introdb_open_data = None

    @property
    def introdb_open_data(self):
        """Load SQLite and gzip support only when the bulk index is actually needed."""
        if self._introdb_open_data is None:
            from resources.lib.introdb_open_data import IntroDBOpenDataAdapter
            self._introdb_open_data = IntroDBOpenDataAdapter()
        return self._introdb_open_data

    def cancel_background_work(self):
        """Cancel the optional bulk sync without creating its adapter at shutdown."""
        if self._introdb_open_data is not None:
            self._introdb_open_data.cancel_sync()
