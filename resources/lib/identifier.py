# -*- coding: utf-8 -*-
"""Playback-scoped detector adapters with lazy loading for the bulk data index."""
import threading

from resources.lib.introdb import IntroDBAdapter
from resources.lib.theintrodb import TheIntroDBAdapter
from resources.lib.chapters import ChaptersAdapter


class Identifier:
    def __init__(self):
        self.introdb_adapter = IntroDBAdapter()
        self.theintrodb_adapter = TheIntroDBAdapter()
        self.chapter_adapter = ChaptersAdapter()
        self._introdb_open_data = None
        self._introdb_lock = threading.Lock()

    @property
    def introdb_open_data(self):
        """Create one shared adapter even when playback and sync race."""
        if self._introdb_open_data is None:
            with self._introdb_lock:
                if self._introdb_open_data is None:
                    from resources.lib.introdb_open_data import IntroDBOpenDataAdapter
                    self._introdb_open_data = IntroDBOpenDataAdapter()
        return self._introdb_open_data

    def cancel_background_work(self):
        """Signal cancellation and return the optional sync thread handle."""
        with self._introdb_lock:
            adapter = self._introdb_open_data
        return adapter.cancel_sync() if adapter is not None else None
